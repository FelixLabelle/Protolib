from collections import defaultdict
from math import log,exp
import pickle
from string import punctuation

from .utils import ProgressBar,mean,n_grammer, PickleBaseClass

# TODO: Add epsilon to avoid numeric issues
eps = 10e-12

class Tokenizer(PickleBaseClass):
    def __init__(self, tokenizer, custom_stoi = None):
        '''
            Inputs:
                tokenizer: function that takes in a string and returns and array of string (tokens)
                custom_stoi: a dictionary that maps strings to numbers, these are your special chars. You can add as many of these as you'd like
            Outputs:
                None
        '''
        self.SOS = "<SOS>"
        self.EOS = "<EOS>"
        self.PAD = "<PAD>"
        self.UNK = "<UNK>"
        if type(custom_stoi) == dict:
            self.stoi = custom_stoi
        else: 
            self.stoi = {self.SOS:0,
            self.EOS:1,
            self.UNK:2,
            self.PAD:3}
            
        self.itos = {}
        self.counts = defaultdict(int)
        self.tokenizer = tokenizer
        
    def train(self, corpus, min_tok_count=1):
        '''
            Inputs:
                corpus: array of strings representing your corpus (each string is an item
                [OPTIONAL] min_tok_count: an integer in range [1,inf] which filters out rare words
            Outputs:
                None
        '''
        assert(type(min_tok_count) == int)
        assert(min_tok_count >= 1)
        for datum in ProgressBar(corpus):
            for token in self.tokenizer(datum):
                self.counts[token] += 1
        
        for token, count in self.counts.items():
            if count >= min_tok_count:
                self.stoi[token] = len(self.stoi)
                
                
        self.itos = {idx:key for key,idx in self.stoi.items()}
        
    def tokenize(self, string):
        return [token if token in self.stoi else self.UNK for token in self.tokenizer(string)]
    
    def encode(self, string):
        return [self.stoi.get(token,self.stoi[self.UNK]) for token in self.tokenizer(string)]
        
    def decode(self, symbols):
        return [self.itos.get(symbol ,self.UNK) for symbol in symbols]
        
    def __len__(self):
        return len(self.stoi)
    
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
    
    def save(self, filename):
        with open(filename +'.pkl','wb') as fh:
            pickle.dump(self.__dict__,fh)
        
    def load(self, filename):
        with open(filename +'.pkl','rb') as fh:
            self.__dict__ = pickle.load(fh)
        
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

def space_split(txt):
    return txt.split()
'''
def punctuation_split(txt):
    tokens = [""]
    for char in txt:
        is_not_white_space = bool(char.strip())
        if char not in punctuation and is_not_white_space:
            tokens[-1] += char
        elif char in punctuation:
            tokens.append(
'''

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
    