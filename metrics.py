from utils import mean

def MSE(xs,x_hats):
    assert(type(xs) == list)
    assert(type(x_hats) == list)
    assert(len(x_hats) == len(xs))
    return mean([(x-x_hat)**2 for x,x_hat in zips(xs,xhats)])

def BLEU(ref_str, comp_str):
    raise NotImplementedError

def ROUGE(ref_str, comp_str):
    raise NotImplementedError
    
def calculateConfusionMatrix(gts,preds):
    raise NotImplementedError
    
