import editdistance
import numpy as np


def jaccard_distance(set1, set2):
    symmetric_difference_ = set1.symmetric_difference(set2)
    union = set1.union(set2)
    if len(union) == 0:
        return 0.0
    return len(symmetric_difference_) / float(len(union))

def get_actual_size(a):
    if isinstance(a, bool):
        return 1.0

    if isinstance(a, int) or isinstance(a, float):
        return abs(float(a))
    
    if isinstance(a, str) or isinstance(a, list) or isinstance(a, set) or isinstance(a, dict):
        return float(len(a))
    
    if isinstance(a, tuple):
        return sum([get_actual_size(val) for val in a])

    try:
        return float(len(a))
    except:
        pass

    try:
        return abs(float(a))
    except:
        pass

    return float(1e+8)

def compare_equal(a, b):
    return float(a != b)

def compare_numbers(a, b):
    return float(abs(a - b))

def compare_bools(a, b):
    return compare_numbers(int(a), int(b))

def compare_strings(a, b):
    return float(editdistance.eval(a, b))

def compare_ranges(a, b):
    return float(editdistance.eval(a, b))

def compare_lists(a, b):
    return float(editdistance.eval([str(val) for val in a], [str(val) for val in b]))

def compare_sets(a, b):
    return jaccard_distance(a, b)

def compare_dicts(a, b):
    return compare_sets(set(a.items()), set(b.items()))

def compare_tuples(a, b):
    length = min(len(a), len(b))

    if len(a) < len(b):
        first, second = a, b
    else:
        first, second = b, a
    
    distance = 0.0
    for i in range(length):
        distance += compare_based_on_type(first[i], second[i])

    for i in range(max(len(a), len(b)) - length):
        distance += get_actual_size(second[length + i])

    return distance

def normalize_value(x):
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, (np.integer, np.int_)):
        return int(x)
    if isinstance(x, (np.floating, np.float_)):
        return float(x)
    if isinstance(x, np.ndarray):
        return normalize_value(x.tolist())  # recursively convert elements
    if isinstance(x, list):
        return [normalize_value(i) for i in x]
    if isinstance(x, tuple):
        return tuple(normalize_value(i) for i in x)
    if isinstance(x, set):
        return {normalize_value(i) for i in x}
    if isinstance(x, dict):
        return {normalize_value(k): normalize_value(v) for k, v in x.items()}
    return x

def compare_based_on_type(a, b):
    a = normalize_value(a)
    b = normalize_value(b)

    if isinstance(a, bool) and isinstance(b, bool):
        return compare_bools(a, b)

    if isinstance(a, bool) and not isinstance(b, bool):
        return None

    if not isinstance(a, bool) and isinstance(b, bool):
        return None

    if isinstance(a, float) and isinstance(b, float):
        a_s = str(a)
        b_s = str(b)
        a_s = a_s[a_s.index('.') + 1:]
        b_s = b_s[b_s.index('.') + 1:]
        d = min(len(a_s), len(b_s))
        return compare_numbers(round(a, d), round(b, d))

    if (isinstance(a, int) or isinstance(a, float)) and (isinstance(b, int) or isinstance(b, float)):
        return compare_numbers(a, b)
    
    if type(a) != type(b):
        return None
    
    if isinstance(a, str):
        return compare_strings(a, b)
    
    if isinstance(a, range):
        return compare_ranges(a, b)
    
    if isinstance(a, list):
        return compare_lists(a, b)
    
    if isinstance(a, set):
        return compare_sets(a, b)
    
    if isinstance(a, dict):
        return compare_dicts(a, b)
    
    if isinstance(a, tuple):
        return compare_tuples(a, b)
    
    try:
        return compare_equal(a, b)
    except:
        pass

    return None
