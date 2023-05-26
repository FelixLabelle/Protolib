import array
import math

from hashes import JenkinsHash
from utils import PickleBaseClass, mean

# This is from a python page, but I converted it to a class
class BitArray:
    def __init__(self, bit_size, fill=0):
        int_size = bit_size >> 5                   # number of 32 bit integers
        if (bit_size & 31):                      # if bit_size != (32 * n) add
            int_size += 1                        #    a record for stragglers
        if fill == 1:
            fill = 4294967295                                 # all bits set
        else:
            fill = 0                                      # all bits cleared

        self.bit_array = array.array('I')          # 'I' = unsigned 32-bit integer

        self.bit_array.extend((fill,) * int_size)

    def testBit(self, bit_num):
        record = bit_num >> 5
        offset = bit_num & 31
        mask = 1 << offset
        return self.bit_array[record] & mask

    # setBit() returns an integer with the bit at 'bit_num' set to 1.
    def setBit(self, bit_num):
        record = bit_num >> 5
        offset = bit_num & 31
        mask = 1 << offset
        self.bit_array[record] |= mask

    # clearBit() returns an integer with the bit at 'bit_num' cleared.
    def clearBit(self, bit_num):
        record = bit_num >> 5
        offset = bit_num & 31
        mask = ~(1 << offset)
        self.bit_array[record] &= mask

    # toggleBit() returns an integer with the bit at 'bit_num' inverted, 0 -> 1 and 1 -> 0.
    def toggleBit(self, bit_num):
        record = bit_num >> 5
        offset = bit_num & 31
        mask = 1 << offset
        self.bit_array[record] ^= mask
    
class BloomFilter(PickleBaseClass):
    def __init__(self, num_hashes, num_bits):
        assert(num_hashes > 0)
        self.num_hashes = num_hashes
        self.hashes = [JenkinsHash(seed) for seed in range(num_hashes)]
        self.num_bits = num_bits
        self.memory = BitArray(self.num_bits) 
        self.num_records = 0
        
    def _hash(self,item):
        return [hash_function(item) % self.num_bits for hash_function in self.hashes]
        
    def insert(self, item):
        hash_values = self._hash(item)
        [self.memory.setBit(val) for val in hash_values]
        self.num_records += 1
    
    def lookup(self, item):
        hash_values = self._hash(item)
        return all([self.memory.testBit(val) for val in hash_values])

    @staticmethod
    def _calculate_num_bits(num_records,false_positive_rate,num_hashes):
        return  -(num_hashes*num_records) /math.log(1 - (false_positive_rate**(1/num_hashes)))  #math.ceil((n * math.log(p)) / math.log(1 / pow(2, math.log(2))))

    @staticmethod
    def _calculate_false_positive_rate(num_hashes,num_records,num_bits):
        return pow(1 - math.exp(-num_hashes / (num_bits / num_records)), num_hashes)
        
    def calculate_false_positive_rate(self):
        return self._calculate_false_positive_rate(self.num_hashes,self.num_records,self.num_bits)
    

class SpaceEfficientBins:
    def __init__(self):
        self.bin_dims = []
        self.bins = []
    
    def _calculate_mse(self, count_data, bin_counts):
        return mean([(bin_counts - count) ** 2 for data,count in count_data.items()])
    
    # HOW TO CALCULATE ERROR ACROSS THE RANGE BOTH THEORITICALLY AND IN PRACTICE
    
    def _train(self, count_data):
        pass
        
    def train(self, count_data):
        pass 
        
if __name__ == "__main__":
    # https://hur.st/bloomfilter/?n=4000&p=1.0E-7&m=&k=20
    
    bloomfilter = BloomFilter(2,32*12)
    bloomfilter.insert("Here")
    import pdb;pdb.set_trace()
    
    # TODO: Add optimization method to find optimal combination of 
    # m and k for a given "N" and "P" value 
    import scipy.optimize as optimize
    import numpy as np
    NUM_ITEMS = 1_000_000
    DESIRED_PROBABILITY = 1e-4
    INITIAL_K = 1
    def optimize_m(input_array):
        #import pdb;pdb.set_trace()
        return BloomFilter._calculate_num_bits(NUM_ITEMS,DESIRED_PROBABILITY,input_array[0])
        
    #import pdb;pdb.set_trace()        
    # ?? Can I limit optimization to integers?
    vals = optimize.minimize(optimize_m,[INITIAL_K],bounds=[(1,100)])

    if vals.success:
        print(f"Optimal value of K found was {vals.x[0]:.2f}")
        def calculate_units(val):
            # Convert bits to bytes
            val_in_units = val/4
            
            curr_unit_idx = 0
            units = ["bytes", "kB","MB","GB","TB","PB"]
            while val_in_units > 1000:
                val_in_units /= 1000
                curr_unit_idx += 1
                
            return val_in_units, units[curr_unit_idx]
        memory_val, val_units = calculate_units(vals.fun)
        print(f"Using {memory_val:.2f} {val_units} of memory")
    else:
        print("Failed to optimize")