from fitness.base_ff_classes.base_ff import base_ff
from utilities.fitness.math_functions import binary_phen_to_float


class binary_phenotype_to_float(base_ff):
    """
    Fitness function for the first problem (T_1) presented in
    [Zitzler2000].
    
    .. Zitzler, Eckart, Kalyanmoy Deb, and Lothar Thiele. Comparison
    of multiobjective evolutionary algorithms: Empirical results.
    Evolutionary computation 8.2 (2000): 173-195.
    """

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

    def evaluate(self, ind, **kwargs):
        min_value = [0] * 30
        max_value = [1] * 30

        real_chromosome = binary_phen_to_float(ind.phenotype, 30, min_value,
                                               max_value)

        return real_chromosome[0]
