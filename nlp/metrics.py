from collections import Counter
import math

from generic.utils import geometric_mean, mean,n_grammer

def MSE(xs,x_hats):
    assert(type(xs) == list and type(x_hats) == list)
    assert(len(x_hats) == len(xs))
    return mean([(x-x_hat)**2 for x,x_hat in zips(xs,xhats)])

def _modifiedNGramPrecision(ref_tokens, comp_tokens,n):
    assert(type(ref_tokens) == list and type(comp_tokens) == list)
    assert(type(n) == int)
    assert(n > 0)
    assert(min(len(ref_tokens),len(comp_tokens)) >= n)
    ref_n_gram_counts = Counter(n_grammer(ref_tokens,n))
    comp_n_gram_counts = Counter(n_grammer(comp_tokens,n))
    union_of_n_grams = set().union(*[ref_n_gram_counts,comp_n_gram_counts])
    return sum(min(comp_n_gram_counts.get(n_gram,0),ref_n_gram_counts.get(n_gram,0)) for n_gram in union_of_n_grams)/sum([comp_n_gram_counts.get(n_gram,0) for n_gram in union_of_n_grams])
    
def _brevityPenalty(ref_tokens, comp_tokens):
    assert(type(ref_tokens) == list and type(comp_tokens) == list)
    num_ref_tokens, num_comp_tokens = len(ref_tokens), len(comp_tokens)
    return math.exp(max(0,(num_ref_tokens/num_comp_tokens)-1))

# TODO: Generalize BLEU to multiple reference sequences
# NOTE: The counts in BLEU could be replaced with an n_gram
# language model which would provide the benefit of smoothing
def BLEU(ref_tokens, comp_tokens,max_n_gram=4,weights=[]):
    assert(type(ref_tokens) == list and type(comp_tokens) == list)
    assert(type(max_n_gram) == int)
    assert(max_n_gram > 0)
    assert(min(len(ref_tokens),len(comp_tokens)) >= max_n_gram)
    assert(type(weights) == list)
    assert(not weights or len(weights) == max_n_gram)
    assert(not weights or sum(weights) == 1)
    if not weights:
        weights = [1/max_n_gram for i in range(1,max_n_gram + 1)]
    bp_val = _brevityPenalty(ref_tokens, comp_tokens)
    n_gram_precisions = [_modifiedNGramPrecision(ref_tokens, comp_tokens,i) for i in range(1,max_n_gram+1)]
    
    # Geometric mean is not well defined for any values lower than zero, so we will automatically return zero
    # if that s the case
    missing_n_gram_overlaps = [n_gram_precision <= 0 for n_gram_precision in n_gram_precisions]
    try:
        if any(missing_n_gram_overlaps):
            raise Warning("There are some lengths of n_gram that have no overlap")
    except Warning as e:
        print(str(e))
    geo_mean = 0 if any(missing_n_gram_overlaps) else geometric_mean(n_gram_precisions,weights=weights)
    return bp_val * geo_mean

def ROUGE(ref_tokens, comp_tokens):
    raise NotImplementedError
    
def calculateConfusionMatrix(gts,preds):
    raise NotImplementedError