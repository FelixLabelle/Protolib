from collections import defaultdict

from .utils import ProgressBar, PickleBaseClass

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

class Tokenizer(PickleBaseClass):
    def __init__(self, tokenizer, additional_special_tokens = None):
        '''
            Inputs:
                tokenizer: function that takes in a string and returns and array of string (tokens)
                custom_stoi: a dictionary that maps strings to numbers, these are your special chars. You can add as many of these as you'd like
            Outputs:
                None
        '''
        self.SOS = "<SOS>"
        self.EOS = "<EOS>"
        self.UNK = "<UNK>"
        self.PAD = "<PAD>"
        
        self.stoi = {self.SOS:0,
        self.EOS:1,
        self.UNK:2,
        self.PAD:3}
        
        if type(additional_special_tokens) == dict:
            self.stoi.update(additional_special_tokens)
            
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
        
    def tokenize(self, string, wrap=False):
        encoded_string = self.encode(string, wrap=wrap)
        return self.decode(encoded_string)
    
    def encode(self, string, wrap=False):
        encoded_string = [self.stoi.get(token,self.stoi[self.UNK]) for token in self.tokenizer(string)]
        if wrap:
            encoded_string = [self.stoi[self.SOS]] + encoded_string + [self.stoi[self.EOS]]
        return encoded_string
        
    def decode(self, symbols):
        return [self.itos.get(symbol ,self.UNK) for symbol in symbols]
        
    def __len__(self):
        return len(self.stoi)
        
class BPE:
    def __init__(self):
        pass
        
    def train(self, data):
        pass
        
    def _pretokenize(self, text):
        pass
        
    def tokenize(self,text):
        pass
        
class WordPiece:
    def __init__(self):
        pass

    def train(self, data):
        pass
        
    def _pretokenize(self, text):
        pass
        
    def tokenize(self,text):
        pass
        
class Unigram:
    def __init__(self):
        pass

    def train(self, data):
        pass
        
    def _pretokenize(self, text):
        pass
        
    def tokenize(self,text):
        pass

# A wrapper around BPE or Unigram that leaves spaces in the vocab
class SentencePiece:
    def __init__(self):
        pass

    def train(self, data):
        pass
        
    def _pretokenize(self, text):
        pass
        
    def tokenize(self,text):
        pass