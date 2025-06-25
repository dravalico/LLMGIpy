#! /usr/bin/env python

from llmpony.pony.utilities.algorithm.general import check_python_version

check_python_version()

import os
import json
from llmpony.pony.algorithm.parameters import params, set_params
from llmpony.pony.utilities.stats.file_io import read_ponyge_results_with_unique_json, create_results_folder_path, BASE_PATH
import sys
from llmpony.pony.representation.individual import Individual
from llmpony.pony.fitness.progimpr import progimpr
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def mane_post():
    set_params(sys.argv[1:])  # exclude the fix_test_timeout.py arg itself

    worst_possible_fitness = float(params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER'])
    res = read_ponyge_results_with_unique_json(base_path=BASE_PATH, params=params, include_seed=True)
    gens = res['gens']
    has_been_fixed = False
    for gen in gens:
        test_fitness = gen['Test fitness']
        l = eval(test_fitness)
        test_fitness_1, test_fitness_2 = float(l[0]), float(l[1])
        train_num_not_passed_cases = float(gen['Training num not passed cases'])
        test_num_not_passed_cases = float(gen['Test num not passed cases'])

        if test_fitness_1 == worst_possible_fitness or test_fitness_2 == worst_possible_fitness or train_num_not_passed_cases == worst_possible_fitness or test_num_not_passed_cases == worst_possible_fitness:
            has_been_fixed = True
            generation = int(gen['Generation'])
            genotype = eval(gen['Genotype'])
            ind = Individual(genotype, None)
            while ind is None or ind.tree is None or ind.phenotype is None or ind.genome is None:
                params['MAX_TREE_DEPTH'] += 10
                if params['MAX_TREE_DEPTH'] >= 90: # SET TO 90 DUE TO PYTHON EVAL() STACK LIMIT.
                    params['MAX_TREE_DEPTH'] = 90
                    ind = Individual(genotype, None)
                    break
                else:
                    ind = Individual(genotype, None)
            ind.phenotype = gen['Phenotype']
            ind.levi_errors = None

            if test_fitness_1 == worst_possible_fitness or test_fitness_2 == worst_possible_fitness:
                temp_fitness_class_instance = progimpr()
                gen['Test fitness'] = str(temp_fitness_class_instance(ind, dist='test', timeout=100.0))
            
            if train_num_not_passed_cases == worst_possible_fitness:
                temp_fitness_file = params['FITNESS_FILE']
                temp_ind_fitness = ind.fitness
                temp_ind_levi_test_fitness = ind.levi_test_fitness
                temp_ind_levi_errors = ind.levi_errors
                
                #params['FITNESS_FILE'] = 'fitness_cases.txt'
                temp_fitness_class_instance = progimpr()
                gen['Training num not passed cases'] = str(temp_fitness_class_instance(ind, dist='training', timeout=100.0)[0])

                params['FITNESS_FILE'] = temp_fitness_file
                ind.fitness = temp_ind_fitness
                ind.levi_test_fitness = temp_ind_levi_test_fitness
                ind.levi_errors = temp_ind_levi_errors

            if test_num_not_passed_cases == worst_possible_fitness:
                temp_fitness_file = params['FITNESS_FILE']
                temp_ind_fitness = ind.fitness
                temp_ind_levi_test_fitness = ind.levi_test_fitness
                temp_ind_levi_errors = ind.levi_errors
                
                #params['FITNESS_FILE'] = 'fitness_cases.txt'
                temp_fitness_class_instance = progimpr()
                gen['Test num not passed cases'] = str(temp_fitness_class_instance(ind, dist='test', timeout=100.0)[0])

                params['FITNESS_FILE'] = temp_fitness_file
                ind.fitness = temp_ind_fitness
                ind.levi_test_fitness = temp_ind_levi_test_fitness
                ind.levi_errors = temp_ind_levi_errors

    if has_been_fixed:
        path = create_results_folder_path(base_path=BASE_PATH, params=params, include_seed=True, make_dirs=False)
        with open(os.path.join(path, 'bests.json'), 'w') as f:
            json.dump({'gens': gens}, f, indent=4)
        print(path)


if __name__ == "__main__":
    mane_post()
