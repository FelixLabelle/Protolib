import pickle

class PickleBaseClass:
    def __init__(self):
        raise NotImplementedError
        
    def save(self, filename):
        with open(filename +'.pkl','wb') as fh:
            pickle.dump(self.__dict__,fh)
        
    def load(self, filename):
        with open(filename +'.pkl','rb') as fh:
            self.__dict__ = pickle.load(fh)
            
def mean(lst):
    return sum(lst)/len(lst)