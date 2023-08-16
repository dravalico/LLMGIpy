from algorithm.parameters import params
from fitness.evaluation import evaluate_fitness
from stats.stats import get_stats, stats
from utilities.stats import trackers

"""Hill-climbing is just about the simplest meta-heuristic there
is. It's of interest in GP/GE because of the lingering suspicion among
many researchers that crossover just doesn't work. This goes back to
90s work by Chellapilla and by O'Reilly. Today, many papers are
published which use mutation only.

Even a simple hill-climber may work well in GP/GE. However, the main
purpose of this module is to provide two modern hill-climbing methods
proposed by Bykov: late-acceptance hill-climbing (LAHC) and
step-counting hill-climbing (SCHC). Both reduce to simple
hill-climbing (HC) with a particular parameter choice, so this module
provides HC as a by-product.

Both LAHC and SCHC are implemented as search_loop-type functions. They
don't provide/require a step-style function. Hence, to use these, just
pass the appropriate dotted function name:

--search_loop algorithm.hill_climbing.LAHC_loop
--search_loop algorithm.hill_climbing.SCHC_loop


LAHC is a hill-climbing algorithm with a history mechanism. The
history mechanism is very simple (one extra parameter: the length of
the history) but in some domains it seems to provide a remarkable
performance improvement compared to hill-climbing itself and other
heuristics. It hasn't previously been used in GP/GE.

LAHC was proposed by Bykov [http://www.cs.nott.ac.uk/~yxb/LAHC/LAHC-TR.pdf].

In standard hill-climbing, where we accept a move to a new proposed
point (created by mutation) if that point is as good as or better than
the current point.

In LAHC, we accept the move if the new point is as good as or better
than that we encountered L steps ago (L for history length).

LAHC is not to be confused with an acceptance to the GECCO
late-breaking papers track.

Step-counting hill-climbing
[http://link.springer.com/article/10.1007/s10951-016-0469-x] is a
variant, proposed by Bykov as an improvement on LAHC. Although less
"natural" it may be slightly simpler to tune again. In SCHC, we
maintain a threshold cost value. We accept moves which are better than
that. We update it every L steps to the current cost value.

There are also two variants: instead of counting all steps, we can
count only accepted, or only improving moves.
"""


def LAHC_search_loop():
    """
    Search loop for Late Acceptance Hill Climbing.
    
    This is the LAHC pseudo-code from Burke and Bykov:

        Produce an initial solution best
        Calculate initial cost function C(best)
        Specify Lfa
        For all k in {0...Lfa-1} f_k := C(best)
        First iteration iters=0;
        Do until a chosen stopping condition
            Construct a candidate solution best*
            Calculate its cost function C(best*)
            idx := iters mod Lfa
            If C(best*)<=f_idx or C(best*)<=C(best)
            Then accept the candidate (best:=best*)
            Else reject the candidate (best:=best)
            Insert the current cost into the fitness array f_idx:=C(best)
            Increment the iteration number iters:=iters+1
    
    :return: The final population.
    """

    max_its = params['POPULATION_SIZE'] * params['GENERATIONS']

    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])

    # Evaluate initial population
    individuals = evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    # Find the best individual so far.
    best = trackers.best_ever

    # Set history.
    Lfa = params['HILL_CLIMBING_HISTORY']
    history = [best for _ in range(Lfa)]

    # iters is the number of individuals examined so far.
    iters = len(individuals)

    for generation in range(1, (params['GENERATIONS'] + 1)):

        this_gen = []

        # even though there is no population, we will take account of
        # the pop size parameter: ie we'll save stats after every
        # "generation"
        for j in range(params['POPULATION_SIZE']):

            this_gen.append(best)  # collect this "generation"

            # Mutate the best to get the candidate best
            candidate_best = params['MUTATION'](best)
            if not candidate_best.invalid:
                candidate_best.evaluate()

            # Find the index of the relevant individual from the late
            # acceptance history.
            idx = iters % Lfa

            if candidate_best >= history[idx]:
                best = candidate_best  # Accept the candidate

            else:
                pass  # reject the candidate

            # Set the new best into the history.
            history[idx] = best

            # Increment evaluation counter.
            iters += 1

            if iters >= max_its:
                # We have completed the total number of iterations.
                break

        # Get stats for this "generation".
        stats['gen'] = generation
        get_stats(this_gen)

        if iters >= max_its:
            # We have completed the total number of iterations.
            break

    return individuals


def SCHC_search_loop():
    """
    Search Loop for Step-Counting Hill-Climbing.
    
    This is the SCHC pseudo-code from Bykov and Petrovic.

        Produce an initial solution best
        Calculate an initial cost function C(best)
        Initial cost bound cost_bound := C(best)
        Initial counter counter := 0
        Specify history
        Do until a chosen stopping condition
            Construct a candidate solution best*
            Calculate the candidate cost function C(best*)
            If C(best*) < cost_bound or C(best*) <= C(best)
                Then accept the candidate best := best*
                Else reject the candidate best := best
            Increment the counter counter := counter + 1
            If counter >= history
                Then update the bound cost_bound := C(best)
                reset the counter counter := 0
        
        Two alternative counting methods (start at the first If):
        
        SCHC-acp counts only accepted moves:
        
            If C(best*) < cost_bound or C(best*) <= C(best)
                Then accept the candidate best := best*
                     increment the counter counter := counter + 1
                Else reject the candidate best := best
            If counter >= history
                Then update the bound cost_bound := C(best)
                     reset the counter counter := 0
        
        SCHC-imp counts only improving moves:
        
            If C(best*) < C(best)
                Then increment the counter counter := counter + 1
            If C(best*) < cost_bound or C(best*) <= C(best)
                Then accept the candidate best := best*
                Else reject the candidate best := best
            If counter >= history
                Then update the bound cost_bound := C(best)
                     reset the counter counter := 0
    
    :return: The final population.
    """

    # Calculate maximum number of evaluation iterations.
    max_its = params['POPULATION_SIZE'] * params['GENERATIONS']
    count_method = params['SCHC_COUNT_METHOD']

    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])

    # Evaluate initial population
    individuals = evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    # Set best individual and initial cost bound.
    best = trackers.best_ever
    cost_bound = best.deep_copy()

    # Set history and counter.
    history = params['HILL_CLIMBING_HISTORY']
    counter = 0

    # iters is the number of individuals examined/iterations so far.
    iters = len(individuals)

    for generation in range(1, (params['GENERATIONS'] + 1)):

        this_gen = []

        # even though there is no population, we will take account of
        # the pop size parameter: ie we'll save stats after every
        # "generation"
        for j in range(params['POPULATION_SIZE']):

            this_gen.append(best)  # collect this "generation"

            # Mutate best to get candidate best.
            candidate_best = params['MUTATION'](best)
            if not candidate_best.invalid:
                candidate_best.evaluate()

            # count
            if count_method == "count_all":  # we count all iterations (moves)
                counter += 1  # increment the counter

            elif count_method == "acp":  # we count accepted moves only
                if candidate_best > cost_bound or candidate_best >= best:
                    counter += 1  # increment the counter

            elif count_method == "imp":  # we count improving moves only
                if candidate_best > best:
                    counter += 1  # increment the counter

            else:
                s = "algorithm.hill_climbing.SCHC_search_loop\n" \
                    "Error: Unknown count method: %s" % (count_method)
                raise Exception(s)

            # accept
            if candidate_best > cost_bound or candidate_best >= best:
                best = candidate_best  # accept the candidate

            else:
                pass  # reject the candidate

            if counter >= history:
                cost_bound = best  # update the bound
                counter = 0  # reset the counter

            # Increment iteration counter.
            iters += 1

            if iters >= max_its:
                # We have completed the total number of iterations.
                break

        # Get stats for this "generation".
        stats['gen'] = generation
        get_stats(this_gen)

        if iters >= max_its:
            # We have completed the total number of iterations.
            break

    return individuals
