import itertools

import numpy as np
from algorithm.parameters import params
from fitness.supervised_learning.supervised_learning import supervised_learning
from utilities.fitness.error_metric import Hamming_error


# import random


class if_else_classifier(supervised_learning):
    """Fitness function for if-else classifier problems. We
    specialise the supervised learning fitness function.

    The user must pass in n_vars, n_is, n_os (number of variables,
    input symbols, output symbols). This is accomplished with, eg,
    --extra_parameters 3 10 2.

    The input and output symbols are just integers. The target
    function is:
    
    ((x[0] + x[1]) % n_os) + 1

    The candidate solutions are like this:

    (3 if x[0] == 2 else (5 if (x[1] == 1 and x[2] == 1) else 9))

    The possible outputs (3, 5, 9) are in the range (0, n_os-1).  The
    inputs (2, 1) are in the range (0, n_is-1). The variables x[i] are
    from x[0] to x[n_vars-1].

    The target function is evaluated at all possible inputs. That
    gives a target dataset for training. There is no test on unseen
    data.

    An example command-line is then:

    python ponyge.py --generations 10 --population 10 --fitness
    supervised_learning.if_else_classifier
    --extra_parameters 3 10 2 --grammar
    supervised_learning/if_else_classifier.bnf

    """

    def __init__(self):
        # Don't call super().__init__() because it reads the training
        # (and test) data from files. We'll do everything else it
        # would have done.

        # we created n, n_is, n_os for convenience, but also the
        # variables with full names hanging on self since grammar.py
        # may need them for GE_RANGE:dataset_n_vars etc.
        n = self.n_vars = int(params['EXTRA_PARAMETERS'][0])
        n_is = self.n_is = int(params['EXTRA_PARAMETERS'][1])
        n_os = self.n_os = int(params['EXTRA_PARAMETERS'][2])

        # Set error metric if it's not set already.
        if params['ERROR_METRIC'] is None:
            params['ERROR_METRIC'] = Hamming_error

        self.maximise = params['ERROR_METRIC'].maximise

        # create the target function
        target = target_classifier(n, n_is, n_os)

        # generate all input combinations for n variables, to become
        # the fitness cases
        Ls = [list(range(n_is)) for i in range(n)]
        X = np.array(list(itertools.product(*Ls)))
        # evaluate the target function at the fitness cases
        self.training_exp = np.array([target(xi) for xi in X])
        self.training_in = X.T

        # In these Classifier problems we don't want a separate test
        # set, and we don't optimize constants.
        assert not params['DATASET_TEST']
        assert not params['OPTIMIZE_CONSTANTS']


def target_classifier(n_vars, n_is, n_os):
    def target(x):
        return ((x[0] + x[1]) % n_os) + 1

    return target
