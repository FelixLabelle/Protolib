import datetime
import math
import pickle
import time

# TODO: Add code to ensure child class defines class variable "_class_version"
# https://stackoverflow.com/questions/22046369/enforcing-class-variables-in-a-subclass
# Inspired by: https://web.archive.org/web/20170707101422/http://pragmaticpython.com/2017/02/03/beeing-defensive-with-pickle-in-evolving-environment/
class PickleBaseClass:
    def __init__(self):
        raise NotImplementedError
        
    def save(self, filename):
        with open(filename +'.pkl','wb') as fh:
            pickle.dump(self.__dict__,fh)
        
    def load(self, filename):
        with open(filename,'rb') as fh:
            self.__dict__ = pickle.load(fh)
            
    def __getstate__(self):
        if not hasattr(self, "_class_version"):
            raise Exception("Your class must define _class_version class variable")
        return dict(_class_version=self._class_version, **self.__dict__)
        
    def __setstate__(self, dict_):
        version_present_in_pickle = dict_.pop("_class_version")
        if version_present_in_pickle != self._class_version:
            raise Exception("Class versions differ: in pickle file: {}, "
                            "in current class definition: {}"
                            .format(version_present_in_pickle,
                                    self._class_version))
def clip(val,limit):
    return min(val,limit)
    
def mean(lst):
    return sum(lst)/len(lst)

def geometric_mean(lst,weights=[],eps=0):
    assert(not weights or len(weights) == len(lst))
    if not weights:
        weights = [1 for i in range(len(lst))]
    return math.exp(mean([weight * math.log(item+eps) for weight, item in zip(weights,lst)]))

def n_grammer(tokens, n):
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-(n-1))]
    
# https://www.youtube.com/watch?v=31Wjc9vZv1s
class ProgressBar:
    def __init__(self, iterable, max_steps=0, display_size=40):
        if max_steps <= 0:
            self.max_steps = len(iterable)
        else:
            self.max_steps = max_steps
        
        self.wrapped_iter = iter(iterable)
        self.display_size = display_size
    
    def _estimate_time(self):
        time_elapsed = time.time() - self.start_time
        average_time_elapsed = time_elapsed/self.current_iter
        estimated_time_remaining = average_time_elapsed * self.max_steps
        time_elapsed_str = datetime.timedelta(seconds=(time_elapsed))
        estimated_time_remaining_str = datetime.timedelta(seconds=(estimated_time_remaining))
        
        return time_elapsed_str, estimated_time_remaining_str
        
    def _print(self):
        percentage_complete = self.current_iter / self.max_steps
        num_symbols = round(self.display_size * percentage_complete)
        time_to_date, time_remaining = self._estimate_time()
        print("[" + "#" * num_symbols + "=" * (self.display_size-num_symbols) + "]" + f" {percentage_complete * 100:.2f}%" + f" {time_to_date}:{time_remaining}",end="\r",sep="")
        
    def __iter__(self):
        self.start_time = time.time()
        self.current_iter = 0
        while self.current_iter < self.max_steps:
            yield next(self.wrapped_iter)
            self.current_iter += 1
            self._print()
        print()
    def __len__(self):
        return self.max_steps