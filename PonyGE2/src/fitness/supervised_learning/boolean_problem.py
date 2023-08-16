import itertools
import random

import numpy as np
from algorithm.parameters import params
from fitness.supervised_learning.supervised_learning import supervised_learning
from utilities.fitness.error_metric import Hamming_error


class boolean_problem(supervised_learning):
    """Fitness function for Boolean problems. We specialise the
    supervised learning fitness function.

    The user must pass in the name of the target function, and n_vars.
    The function is created. It is evaluated at all possible
    inputs. That gives a target dataset for training. This is
    accomplished with, eg, --extra_parameters nparity 5. There is
    no test on unseen data.

    An example command-line is then:

    python ponyge.py --generations 10 --population 10 --fitness
    supervised_learning.boolean_problem
    --extra_parameters nparity 3 --grammar
    supervised_learning/boolean.bnf

    """

    def __init__(self):
        # Don't call super().__init__() because it reads the training
        # (and test) data from files. We'll do everything else it
        # would have done.

        target_name = params['EXTRA_PARAMETERS'][0]

        # may be needed if the grammar uses GE_RANGE:dataset_n_vars
        n = self.n_vars = int(params['EXTRA_PARAMETERS'][1])

        # Set error metric if it's not set already.
        if params['ERROR_METRIC'] is None:
            params['ERROR_METRIC'] = Hamming_error

        self.maximise = params['ERROR_METRIC'].maximise

        # create the target function
        if target_name == "random_boolean":
            target = make_random_boolean_fn(n)
        else:
            target = eval(target_name)

        # generate all input combinations for n variables, to become
        # the fitness cases
        Ls = [[False, True] for i in range(n)]
        X = np.array(list(itertools.product(*Ls)))
        # evaluate the target function at the fitness cases
        self.training_exp = np.array([target(xi) for xi in X])
        self.training_in = X.T

        # In Boolean problems we don't want a separate test set
        assert not params['DATASET_TEST']


# Some target functions. Each just accepts a single instance, eg
# nparity([False, False, True]) -> True

def boolean_true(x):
    return True


def comparator(x):
    """Comparator function: input consists of two n-bit numbers. Output is
    0 if the first is larger or equal, or 1 if the second is larger."""
    assert len(x) % 2 == 0
    n = len(x) // 2
    # no need to convert from binary. just use list comparison
    return x[:n] < x[n:]


def multiplexer(x):
    """Multiplexer: a address bits and 2^a data bits. n = a + 2^a. Output
    the value of the data bit addressed by the address bits.
    """
    if len(x) == 1 + 2 ** 1:
        a = 1  # 2
    elif len(x) == 2 + 2 ** 2:
        a = 2  # 6
    elif len(x) == 3 + 2 ** 3:
        a = 3  # 11
    elif len(x) == 4 + 2 ** 4:
        a = 4  # 20
    elif len(x) == 5 + 2 ** 5:
        a = 5  # 37
    elif len(x) == 6 + 2 ** 6:
        a = 6  # 70
    else:
        raise ValueError(x)
    addr = binlist2int(x[:a])  # get address bits, convert to int
    return x[a + addr]  # which data bit? offset by a


def nparity(x):
    'Parity function of any number of input variables'
    return x.sum() % 2 == 1


# special target function: random truth table
def make_random_boolean_fn(n):
    """Make a random Boolean function of n variables."""
    outputs = [random.choice([False, True])
               for i in range(2 ** n)]

    def f(x):
        return outputs[binlist2int(x)]

    return f


# Helper function

def binlist2int(x):
    """Convert a list of binary digits to integer"""
    return int("".join(map(str, map(int, x))), 2)
