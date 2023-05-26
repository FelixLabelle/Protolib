from collections import defaultdict
from math import log,exp

from generic.utils import ProgressBar,mean,n_grammer, PickleBaseClass
from tokenizers import Tokenizer

# TODO: Add epsilon to avoid numeric issues
eps = 10e-12
    
class NGramLM(PickleBaseClass):
    def __init__(self, n):
        assert(type(n) == int)
        assert(n >= 1)
        self.n = n
        
    def _preprocess_text(self, text):
        tokens = self.tokenizer.tokenize(text)
        tokens = ([self.tokenizer.SOS] * (self.n-1)) + tokens + ([self.tokenizer.EOS] * (self.n-1))
        return n_grammer(tokens,self.n)
        
    def train(self, corpus, tokenizer):
        assert(type(tokenizer) == Tokenizer)
        # TODO: Add a way to prune data
        self.tokenizer = tokenizer
        self.context_counts = defaultdict(int)
        self.ngram_counts = defaultdict(int)
        for datum in ProgressBar(corpus):
            for n_gram in self._preprocess_text(datum):
                self.context_counts[n_gram[:self.n-1]]+= 1
                self.ngram_counts[n_gram]+= 1
        
        # To avoid returning default value
        self.ngram_counts = dict(self.ngram_counts)
        self.context_counts = dict(self.context_counts)
        
    def __call__(self, n_gram):
        assert(len(n_gram) == self.n and type(n_gram) == tuple)
        assert(self.ngram_counts and self.context_counts)
        return log(self.ngram_counts[n_gram]/self.context_counts[n_gram[:self.n-1]])
    
    def calculate_perplexity(self, text):
        n_grams = self._preprocess_text(text)
        return exp(-mean([self.__call__(n_gram) for n_gram in n_grams]))
        
class AddKSmoothingNGramLM(NGramLM):
    def __init__(self, n,k):
        assert(type(k) == float or type(k) == int)
        assert(k > 0)
        self.k = k
        super().__init__(n)
        
    def __call__(self, n_gram):
        assert(len(n_gram) == self.n and type(n_gram) == tuple)
        assert(self.ngram_counts and self.context_counts)
        return log((self.ngram_counts.get(n_gram,0) + self.k)/(self.context_counts.get(n_gram[:self.n-1],0) + (self.k * len(self.tokenizer))))

class LaplaceSmoothingNGramLM(AddKSmoothingNGramLM):
    def __init__(self, n):
        super().__init__(n,1)
        
class BackOffNGramLM(NGramLM):
    def __init__(self, n):
        super().__init__(n)
        
    
    def train(self,corpus, tokenizer):
        self.tokenizer = tokenizer
        self.lms = [NGramLM(i) for i in range(1,self.n+1)]
        [lm.train(corpus,tokenizer) for lm in ProgressBar(self.lms)]
        
    def __call__(self, n_gram):
        assert(len(n_gram) == self.n)
        for i in range(self.n,0,-1):
            try:
                log_prob = self.lms[i-1](n_gram[-i:])
                break
            except KeyError as k:
                pass
        return log_prob

class InterpolatedNGramLM(NGramLM):
    def __init__(self, n):
        super().__init__(n)
        
        
    
    def train(self,corpus, tokenizer, dev_corpus=[]):
        self.tokenizer = tokenizer
        self.lms = [NGramLM(i) for i in range(1,self.n+1)]
        [lm.train(corpus,tokenizer) for lm in ProgressBar(self.lms)]
        # TODO: Add a way of learning interpolation weights
        if dev_corpus:
            pass
        else:
            self.weights = [1 for i in range(1,self.n+1)]
            
    def __call__(self, n_gram):
        assert(len(n_gram) == self.n)
        vals = []
        for i in range(self.n,0,-1):
            try:
                log_prob = self.lms[i-1](n_gram[-i:])
                vals = log_prob * self.weights[i]
            except KeyError as k:
                vals = eps
        return sum(vals)
        
# TODO: Add kneser-neys


if __name__ == "__main__":
    import pdb;pdb.set_trace()
    from nltk import word_tokenize
    # "babylm_dev_v1.dev"
    LOWER_CASE = True
    corpus = [line.strip() for line in open("dedupe_shuffled_window4_v4.train" , 'r', encoding="utf=8").readlines()]
    if LOWER_CASE:
        corpus = [datum.lower() for datum in corpus]
    # ["Here is a test sentence", "Here is another test sentence a"]
    tokenizer = Tokenizer(word_tokenize)
    # NOTE: The min token count will be sum(range(WINDOW_SIZE,1,-1))* 20 
    # Windowing greatly increase the number of times a token will appear
    tokenizer.train(corpus,min_tok_count=180)
    print(len(tokenizer),len(tokenizer)/len(tokenizer.counts))
    lm = BackOffNGramLM(4)
    lm.train(corpus, tokenizer)
    lm.save("Babylm_train_backoff_four_gram_v1")
    # TODO: Add ability to save LM
    print(lm.calculate_perplexity(corpus[180]))
    print(corpus[180])
    