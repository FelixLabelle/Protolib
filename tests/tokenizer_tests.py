import unittest

from generic.file_utils import load_jsonl
from nlp.tokenizers import Tokenizer, space_split, punc_split

# How easy would it be to generate a large suite..
class TokenizerTestCase(unittest.TestCase):
    def __init__(self, tokenizer, test_case, methodName='runTest'):
        super().__init__(methodName)
        self.tokenizer = tokenizer
        self._id = "placeholder"
        self.test_case = test_case
        
    def runTest(self):
        input_text = self.test_case["input_text"]
        if not self.tokenizer._trained:
            self.tokenizer.train([input_text])
        
        expected_tokens = self.test_case["expected_tokens"]
        tokens = self.tokenizer.tokenize(input_text)
        self.assertEqual(tokens, expected_tokens)

if __name__ == '__main__':
    # Instantiate the tokenizer objects
    #tokenizer1 = Tokenizer(space_split)
    tokenizer1 = Tokenizer(punc_split)
    examples = load_jsonl("tests/tokenizer_test_examples.jsonl")
    from collections import defaultdict
    
    example_suites = defaultdict(list)
    for example in examples:
        example_suites[example["test_type"]].append(example)
    # TODO: Group examples based on test type
    # Each name should be a suite
    # We could summarize percentages
    # Combine the test suites
    suite_results = defaultdict(unittest.TestResult)
    suite_stats = defaultdict(dict)
    for test_type, example_suite in example_suites.items():
        print(test_type)
        all_suites = unittest.TestSuite([TokenizerTestCase(Tokenizer(punc_split), example) for example in example_suite])
        all_suites.run(suite_results[test_type])
        results = suite_results[test_type]
        suite_stats[test_type]['Support'] = suite_results[test_type].testsRun
        suite_stats[test_type]['Percentage Failed'] = len(suite_results[test_type].failures)/suite_results[test_type].testsRun

    print(suite_stats)
    # Run the test suites
    # Is verbose and shows errors
    # TODO: Is there a way of saving this info?
    
    
    
