from multiprocessing import cpu_count
from os import path
from socket import gethostname

hostname = gethostname().split('.')
machine_name = hostname[0]

"""Algorithm parameters"""
params = {
    # Set default step and search loop functions
    'SEARCH_LOOP': 'search_loop',
    'STEP': 'step',

    # Evolutionary Parameters
    'POPULATION_SIZE': 500,
    'GENERATIONS': 50,
    'HILL_CLIMBING_HISTORY': 1000,
    'SCHC_COUNT_METHOD': "count_all",

    # Set optional experiment name
    'EXPERIMENT_NAME': None,
    # Set default number of runs to be done.
    # ONLY USED WITH EXPERIMENT MANAGER.
    'RUNS': 1,

    # Class of problem
    'FITNESS_FUNCTION': "supervised_learning.regression",
    'FITNESS_FILE': None,

    # Select problem dataset
    'DATASET_TRAIN': "Vladislavleva4/Train.txt",
    'DATASET_TEST': None,
    'DATASET_DELIMITER': None,

    # Set grammar file
    'GRAMMAR_FILE': "supervised_learning/Vladislavleva4.bnf",

    # Set the number of depths permutations are calculated for
    # (starting from the minimum path of the grammar).
    # Mainly for use with the grammar analyser script.
    'PERMUTATION_RAMPS': 5,

    # Select error metric
    'ERROR_METRIC': None,

    # Optimise constants in the supervised_learning fitness function.
    'OPTIMIZE_CONSTANTS': False,

    # Specify target for target problems
    'TARGET': "ponyge_rocks",

    # Set max sizes of individuals
    'MAX_TREE_DEPTH': 90,  # SET TO 90 DUE TO PYTHON EVAL() STACK LIMIT.
    # INCREASE AT YOUR OWN RISK.
    'MAX_TREE_NODES': None,
    'CODON_SIZE': 100000,
    'MAX_GENOME_LENGTH': None,
    'MAX_WRAPS': 0,

    # INITIALISATION
    # Set initialisation operator.
    'INITIALISATION': "operators.initialisation.PI_grow",
    # Set the maximum genome length for initialisation.
    'INIT_GENOME_LENGTH': 200,
    # Set the maximum tree depth for initialisation.
    'MAX_INIT_TREE_DEPTH': 10,
    # Set the minimum tree depth for initialisation.
    'MIN_INIT_TREE_DEPTH': None,

    # SELECTION
    # Set selection operator.
    'SELECTION': "operators.selection.tournament",
    # For tournament selection
    'TOURNAMENT_SIZE': 2,
    # For truncation selection
    'SELECTION_PROPORTION': 0.5,
    # Allow for selection of invalid individuals during selection process.
    'INVALID_SELECTION': False,

    # OPERATOR OPTIONS
    # Boolean flag for selecting whether or not mutation is confined to
    # within the used portion of the genome. Default set to True.
    'WITHIN_USED': True,

    # CROSSOVER
    # Set crossover operator.
    'CROSSOVER': "operators.crossover.variable_onepoint",
    # Set crossover probability.
    'CROSSOVER_PROBABILITY': 0.75,
    # Prevents crossover from generating invalids.
    'NO_CROSSOVER_INVALIDS': False,

    # MUTATION
    # Set mutation operator.
    'MUTATION': "operators.mutation.int_flip_per_codon",
    # Set mutation probability (None defaults to 1 over the length of
    # the genome for each codon)
    'MUTATION_PROBABILITY': None,
    # Set number of mutation events
    'MUTATION_EVENTS': 1,
    # Prevents mutation from generating invalids.
    'NO_MUTATION_INVALIDS': False,

    # REPLACEMENT
    # Set replacement operator.
    'REPLACEMENT': "operators.replacement.generational",
    # Set elite size.
    'ELITE_SIZE': None,

    # DEBUGGING
    # Use this to turn on debugging mode. This mode doesn't write any files
    # and should be used when you want to test new methods.
    'DEBUG': False,

    # PRINTING
    # Use this to print out basic statistics for each generation to the
    # command line.
    'VERBOSE': False,
    # Use this to prevent anything being printed to the command line.
    'SILENT': False,

    # SAVING
    # Save the phenotype of the best individual from each generation. Can
    # generate a lot of files. DEBUG must be False.
    'SAVE_ALL': False,
    # Save a plot of the evolution of the best fitness result for each
    # generation.
    'SAVE_PLOTS': True,

    # MULTIPROCESSING
    # Multi-core parallel processing of phenotype evaluations.
    'MULTICORE': False,
    # Set the number of cpus to be used for multiprocessing
    'CORES': cpu_count(),

    # STATE SAVING/LOADING
    # Save the state of the evolutionary run every generation. You can
    # specify how often you want to save the state with SAVE_STATE_STEP.
    'SAVE_STATE': False,
    # Specify how often the state of the current evolutionary run is
    # saved (i.e. every n-th generation). Requires int value.
    'SAVE_STATE_STEP': 1,
    # Load an evolutionary run from a saved state. You must specify the
    # full file path to the desired state file. Note that state files have
    # no file type.
    'LOAD_STATE': None,

    # SEEDING
    # Specify a list of PonyGE2 individuals with which to seed the initial
    # population.
    'SEED_INDIVIDUALS': [],
    # Specify a target seed folder in the 'seeds' directory that contains a
    # population of individuals with which to seed a run.
    'TARGET_SEED_FOLDER': None,
    # Set a target phenotype string for reverse mapping into a GE
    # individual
    'REVERSE_MAPPING_TARGET': None,
    # Set Random Seed for all Random Number Generators to be used by
    # PonyGE2, including the standard Python RNG and the NumPy RNG.
    'RANDOM_SEED': None,

    # CACHING
    # The cache tracks unique individuals across evolution by saving a
    # string of each phenotype in a big list of all phenotypes. Saves all
    # fitness information on each individual. Gives you an idea of how much
    # repetition is in standard GE/GP.
    'CACHE': False,
    # Uses the cache to look up the fitness of duplicate individuals. CACHE
    # must be set to True if you want to use this.
    'LOOKUP_FITNESS': False,
    # Uses the cache to give a bad fitness to duplicate individuals. CACHE
    # must be True if you want to use this (obviously)
    'LOOKUP_BAD_FITNESS': False,
    # Removes duplicate individuals from the population by replacing them
    # with mutated versions of the original individual. Hopefully this will
    # encourage diversity in the population.
    'MUTATE_DUPLICATES': False,

    # MULTI-AGENT Parameters
    # True or False for multi-agent
    'MULTIAGENT': False,
    # Agent Size. Number of agents having their own copy of genetic material
    'AGENT_SIZE': 100,
    # Interaction Probability: how frequently the agents can interaction with
    # each other
    'INTERACTION_PROBABILITY': 0.5,

    # OTHER
    # Set machine name (useful for doing multiple runs)
    'MACHINE': machine_name
}


def load_params(file_name):
    """
    Load in a params text file and set the params dictionary directly.

    :param file_name: The name/location of a parameters file.
    :return: Nothing.
    """
    
    try:
        open(file_name, "r")
    except FileNotFoundError:
        s = "algorithm.parameters.load_params\n" \
            "Error: Parameters file not found.\n" \
            "       Ensure file extension is specified, e.g. 'regression.txt'."
        raise Exception(s)

    with open(file_name, 'r') as parameters:
        # Read the whole parameters file.
        content = parameters.readlines()

        for line in [l for l in content if not l.startswith("#")]:

            # Parameters files are parsed by finding the first instance of a
            # colon.
            split = line.find(":")

            # Everything to the left of the colon is the parameter key,
            # everything to the right is the parameter value.
            key, value = line[:split], line[split + 1:].strip()

            # Evaluate parameters.
            try:
                value = eval(value)

            except:
                # We can't evaluate, leave value as a string.
                pass

            # Set parameter
            params[key] = value


def set_params(command_line_args, create_files=True):
    """
    This function parses all command line arguments specified by the user.
    If certain parameters are not set then defaults are used (e.g. random
    seeds, elite size). Sets the correct imports given command line
    arguments. Sets correct grammar file and fitness function. Also
    initialises save folders and tracker lists in utilities.trackers.

    :param command_line_args: Command line arguments specified by the user.
    :return: Nothing.
    """
    
    from utilities.algorithm.initialise_run import initialise_run_params
    from utilities.algorithm.initialise_run import set_param_imports
    from utilities.fitness.math_functions import return_one_percent
    from utilities.algorithm.command_line_parser import parse_cmd_args
    from utilities.stats import trackers, clean_stats
    from representation import grammar

    cmd_args, unknown = parse_cmd_args(command_line_args)

    if unknown:
        # We currently do not parse unknown parameters. Raise error.
        s = "algorithm.parameters.set_params\nError: " \
            "unknown parameters: %s\nYou may wish to check the spelling, " \
            "add code to recognise this parameter, or use " \
            "--extra_parameters" % str(unknown)
        raise Exception(s)

    # LOAD PARAMETERS FILE
    # NOTE that the parameters file overwrites all previously set parameters.
    if 'PARAMETERS' in cmd_args:
        load_params(path.join("..", "parameters", cmd_args['PARAMETERS']))

    # Join original params dictionary with command line specified arguments.
    # NOTE that command line arguments overwrite all previously set parameters.
    params.update(cmd_args)

    if params['LOAD_STATE']:
        # Load run from state.
        from utilities.algorithm.state import load_state

        # Load in state information.
        individuals = load_state(params['LOAD_STATE'])

        # Set correct search loop.
        from algorithm.search_loop import search_loop_from_state
        params['SEARCH_LOOP'] = search_loop_from_state

        # Set population.
        setattr(trackers, "state_individuals", individuals)

    else:
        if params['REPLACEMENT'].split(".")[-1] == "steady_state":
            # Set steady state step and replacement.
            params['STEP'] = "steady_state_step"
            params['GENERATION_SIZE'] = 2

        else:
            # Elite size is set to either 1 or 1% of the population size,
            # whichever is bigger if no elite size is previously set.
            if params['ELITE_SIZE'] is None:
                params['ELITE_SIZE'] = return_one_percent(1, params[
                    'POPULATION_SIZE'])

            # Set the size of a generation
            params['GENERATION_SIZE'] = params['POPULATION_SIZE'] - \
                params['ELITE_SIZE']

        if (params['MUTATION_PROBABILITY'] is not None and
                params['MUTATION_EVENTS'] != 1):
            s = "operators.mutation.int_flip_per_codon\n" \
                "Error: mutually exclusive parameters 'MUTATION_PROBABILITY'" \
                "and 'MUTATION_EVENTS' have been explicitly set.\n" \
                "Only one of these parameters can be used at a time."
            raise Exception(s)

        # Initialise run lists and folders before we set imports.r
        initialise_run_params(create_files)

        # Set correct param imports for specified function options, including
        # error metrics and fitness functions.
        set_param_imports()

        # Clean the stats dict to remove unused stats.
        clean_stats.clean_stats()

        # Set GENOME_OPERATIONS automatically for faster linear operations.
        if (params['CROSSOVER'].representation == "subtree" or
                params['MUTATION'].representation == "subtree"):
            params['GENOME_OPERATIONS'] = False
        else:
            params['GENOME_OPERATIONS'] = True

        # Ensure correct operators are used if multiple fitness functions used.
        if hasattr(params['FITNESS_FUNCTION'], 'multi_objective'):

            # Check that multi-objective compatible selection is specified.
            if not hasattr(params['SELECTION'], "multi_objective"):
                s = "algorithm.parameters.set_params\n" \
                    "Error: multi-objective compatible selection " \
                    "operator not specified for use with multiple " \
                    "fitness functions."
                raise Exception(s)

            if not hasattr(params['REPLACEMENT'], "multi_objective"):

                # Check that multi-objective compatible replacement is
                # specified.
                if not hasattr(params['REPLACEMENT'], "multi_objective"):
                    s = "algorithm.parameters.set_params\n" \
                        "Error: multi-objective compatible replacement " \
                        "operator not specified for use with multiple " \
                        "fitness functions."
                    raise Exception(s)

        # Parse grammar file and set grammar class.
        params['BNF_GRAMMAR'] = grammar.Grammar(
            path.join("..", "grammars", params['GRAMMAR_FILE']))

        # If OPTIMIZE_CONSTANTS, check that the grammar is suitable
        if params['OPTIMIZE_CONSTANTS']:
            if "c[" not in params['BNF_GRAMMAR'].terminals:
                raise ValueError("Grammar unsuitable for OPTIMIZE_CONSTANTS")

        # Population loading for seeding runs (if specified)
        if params['TARGET_SEED_FOLDER']:

            # Import population loading function.
            from operators.initialisation import load_population

            # A target folder containing seed individuals has been given.
            params['SEED_INDIVIDUALS'] = load_population(
                params['TARGET_SEED_FOLDER'])
            for ind in params['SEED_INDIVIDUALS']:
                print(ind.phenotype)

        elif params['REVERSE_MAPPING_TARGET']:
            # A single seed phenotype has been given. Parse and run.

            # Import GE LR Parser.
            from scripts import GE_LR_parser

            # Parse seed individual and store in params.
            params['SEED_INDIVIDUALS'] = [GE_LR_parser.main()]
