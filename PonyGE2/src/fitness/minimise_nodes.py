from fitness.base_ff_classes.base_ff import base_ff


class minimise_nodes(base_ff):
    """
    Fitness function class for minimising the number of nodes in a
    derivation tree.
    """

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

    def evaluate(self, ind, **kwargs):
        return ind.nodes
