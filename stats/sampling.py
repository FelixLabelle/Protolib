
def reservoir_sampling_algorithm_r(stream,number_samples,max_size=-1, custom_error_handling=None):
    i = 0
    stream_terminated = False
    sample = []
    while not stream_terminated and (i < max_size or max_size == -1):
        if i < number_samples:
            try:
                sample.append(next(stream))
            except StopIteration:
                stream_terminated = True
                raise ValueError(f"Expected a stream of atleast {number_samples}, recieved {i}")
        else:
            replacement_idx = random.randint(0,i)
            if replacement_idx < number_samples:
                try:
                    sample[replacement_idx] = next(stream)
                except StopIteration:
                   stream_terminated = True 
                except Exception as e:
                    if custom_error_handling:
                        custom_error_handling(e)
                    else:
                        raise e
        i += 1
    return sample
    
    
def reservoir_sampling_algorithm_l(stream,number_samples,max_size=-1, custom_error_handling=None):
    i = 0
    stream_terminated = False
    sample = []
    jump_size_weight = math.exp(math.log(random.random())/number_samples)
    while not stream_terminated and (i < max_size or max_size == -1):
        if i < number_samples:
            try:
                data = next(stream)
                sample.append(data)
                i += 1
            except StopIteration:
                stream_terminated = True
                raise ValueError(f"Expected a stream of atleast {number_samples}, recieved {i}")
            except Exception as e:
                if custom_error_handling:
                    custom_error_handling(e)
                else:
                    raise e
        else:
            # The larger the numerator the larger the skip (low random values prelog)
            # The smaller the denominator the  the skip (we lower jumpsize as get further along to achieve this)
            number_of_jumps = math.floor(math.log(random.random())/math.log(1-jump_size_weight))
            for _ in range(number_of_jumps):
                try:
                    next(stream)
                    i += 1
                except StopIteration:
                    stream_terminated = True
            if not stream_terminated:
                # Randomly replace previous data
                try:
                    sample[random.randint(0,number_samples-1)] = next(stream)
                    # This continually decreases the jump_size_weight, in term decreasing jump size
                    # This makes sure we don't over favor items earlier on in the data
                    jump_size_weight = jump_size_weight * math.exp(math.log(random.random())/number_samples)
                    i += 1
                except StopIteration:
                    stream_terminated=True
                except Exception as e:
                    if custom_error_handling:
                        custom_error_handling(e)
                    else:
                        raise e
    return sample