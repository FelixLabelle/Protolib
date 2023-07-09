from collections import Counter, defaultdict

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
    assert(all([key in x_values for key in x_counts))
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