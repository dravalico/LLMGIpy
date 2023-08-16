import numpy as np

np.seterr(all="raise")


class base_ff:
    """
    Base fitness function class from which all fitness functions inherit.
    
    This is an abstract class which exists just to be subclassed; it should not
    be instantiated.
    """

    # Default default fitness function is NaN.
    default_fitness = np.NaN

    # Default fitness objective is to minimise fitness.
    maximise = False

    def __init__(self):
        pass

    def __call__(self, ind, **kwargs):
        """
        

        :param ind: An individual to be evaluated.
        :return: The fitness of the evaluated individual.
        """

        try:
            # Evaluate the fitness using the evaluate() function. This function
            # can be over-written by classes which inherit from this base
            # class.
            fitness = self.evaluate(ind, **kwargs)

        except (FloatingPointError, ZeroDivisionError, OverflowError,
                MemoryError):
            # FP err can happen through eg overflow (lots of pow/exp calls)
            # ZeroDiv can happen when using unprotected operators
            fitness = base_ff.default_fitness

            # These individuals are valid (i.e. not invalids), but they have
            # produced a runtime error.
            ind.runtime_error = True

        except Exception as err:
            # Other errors should not usually happen (unless we have
            # an unprotected operator) so user would prefer to see them.
            print(err)
            raise

        return fitness

    def evaluate(self, ind, **kwargs):
        """
        Default fitness execution call for all fitness functions. When
        implementing a new fitness function, merely over-write this function
        in your own fitness function. All fitness functions must inherit from
        the base fitness function class.
        
        :param ind: An individual to be evaluated.
        :param kwargs: Optional extra arguments.
        :return: The fitness of the evaluated individual.
        """

        # Evaluate the fitness of the phenotype
        fitness = eval(ind.phenotype)

        return fitness
