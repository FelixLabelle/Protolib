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

# https://www.youtube.com/watch?v=31Wjc9vZv1s
class ProgressBar:
    def __init__(self, iterable, max_steps=0):
        if max_steps <= 0:
            self.max_steps = len(iterable)
        else:
            self.max_steps = max_steps
        self.current_iter = 0
        self.wrapped_iter = iter(iterable)
        self.print_size = 20
        
    def _print(self):
        percentage_complete = self.current_iter / self.max_steps
        num_symbols = round(self.print_size * percentage_complete)
        
        print("[" + "#" * num_symbols + "=" * (self.print_size-num_symbols) + "]" + f" {percentage_complete * 100:.2f}%",end="\r",sep="")
        
    def __iter__(self):
        while self.current_iter < self.max_steps:
            self._print()
            yield next(self.wrapped_iter)
            self.current_iter += 1
        print()
    def __len__(self):
        return self.max_steps