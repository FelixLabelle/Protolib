from collections import Counter, defaultdict

import sys
sys.path.append('..')
from generic.data_structures import BinaryTree, BitArray
from generic.utils import PickleBaseClass

def discrete_joint_entropy(x_y_counts,x_values,y_values):
	assert(type(x_y_counts) in [Counter, defaultdict,dict])
	assert(type(y_values) == list)
	assert(type(x_values) == list)
	assert(all([type(key) == tuple for key in x_y_counts.keys()]))
	num_events = sum(x_y_counts.values())
	probs = {val: count/num_events for val,count in x_y_counts.items()}
	def inner_term(x,y):
		count = x_y_counts.get((x,y),0)
		inner_term_val = 0
		if count > 0:
			prob = probs[(x,y)]
			inner_term_val = prob * math.log2(prob)
		elif count < 0:
			raise ValueError("Expected positive count...")
		return inner_term_val
	entropy = -sum([inner_term(x,y) for x,y in itertools.product(x_values,y_values)])
	return entropy

def discrete_entropy(x_counts,x_values):
	assert(type(x_counts) in [Counter, defaultdict,dict])
	assert(type(x_values) == list)
	assert(all([key in x_values for key in x_counts]))
	num_events = sum(x_counts.values())
	probs = {val: count/num_events for val,count in x_counts.items()}
	def inner_term(x):
		count = x_counts.get(x,0)
		inner_term_val = 0
		if count > 0:
			prob = probs[x]
			inner_term_val = prob * math.log2(prob)
		elif count < 0:
			raise ValueError("Expected positive count...")
		return inner_term_val
	entropy = -sum([inner_term(x) for x in x_values])
	return entropy

# TODO: Convert to use a bitstring instead of strings..
class HuffmanTree(PickleBaseClass):
	_class_version = "0.0.1"
	def __init__(self):
		self.dictionary = set()
		self.tree = BinaryTree()
		self.encoding_lut = {} # NOTE: To improve speed you just store a symbol to byte string mapping here
		
	def learn(self,symbols):
		# get counts for each symbols
		symbol_counts = Counter(symbols)
		# create a dict of nodes, with counts for each node
		nodes = [{"symbol" : symbol, "count": count} for symbol,count in symbol_counts.items()]
		nodes = sorted(nodes,key=lambda node: node['count'],reverse=True)
		while len(nodes) > 1:
			new_node = BinaryTree()
			new_node.r_child = nodes.pop(-1)
			new_node.l_child = nodes.pop(-1)
			new_node['count'] = new_node.r_child['count'] + new_node.l_child['count']
			nodes.append(new_node)
			nodes = sorted(nodes,key=lambda node: node['count'],reverse=True)
		assert(len(nodes) == 1)
		self.dictionary = set(symbol_counts.keys())
		self.tree = nodes[0]
		for symbol_dict, path in self.tree.traverse():
			self.encoding_lut[symbol_dict['symbol']] = path
		# TODO: Create symbol to byte_string mapping here
		# Traverse the tree, return each node you come across with a string
		# describing it's location (l = 0, r = 1)
		
		
		
	def encode(self, string):
		byte_string = ''
		for symbol in string:
			byte_string += self.encoding_lut[symbol]
		return byte_string
		
	def decode(self, byte_string):
		symbols = []
		current_tree_node = self.tree
		for byte in byte_string:
			if byte == '0':
				current_tree_node = current_tree_node.l_child
			elif byte == '1':
				current_tree_node = current_tree_node.r_child
			else:
				raise ValueError(f"Expected either 0 or 1, recieved {byte}")
			
			if type(current_tree_node) != BinaryTree:
				symbols.append(current_tree_node['symbol'])
				current_tree_node = self.tree
			else:
				#import pdb;pdb.set_trace()
				pass
		return symbols
		
if __name__ == "__main__":
	huffman_tree = HuffmanTree()
	tst_str = "here is a test string.Here is yet another test string that's a little bit longer and something about a lazy brown fox."
	huffman_tree.learn(tst_str)
	encoded_tst_str = huffman_tree.encode(tst_str)
	decoded_tst_str = huffman_tree.decode(encoded_tst_str)
	decoded_tst_str = "".join(decoded_tst_str)
	print(decoded_tst_str)
	assert(decoded_tst_str == tst_str)