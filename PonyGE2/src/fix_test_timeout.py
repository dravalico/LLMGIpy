#! /usr/bin/env python

from utilities.algorithm.general import check_python_version

check_python_version()

from algorithm.parameters import params, set_params
from utilities.stats.file_io import read_ponyge_results, create_results_folder_path, BASE_PATH
import sys
from representation.individual import Individual
from fitness.progimpr import progimpr
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

def mane_post():
    set_params(sys.argv[1:])  # exclude the fix_test_timeout.py arg itself

    worst_possible_fitness = float(params['WORST_POSSIBLE_FITNESS'])
    res = read_ponyge_results(base_path=BASE_PATH, params=params, include_seed=True)
    gens = res['gens']
    for gen in gens:
        test_fitness = float(gen['Test fitness:'])
        train_num_not_passed_cases = float(gen['Training num not passed cases:'])
        test_num_not_passed_cases = float(gen['Test num not passed cases:'])

        if test_fitness == worst_possible_fitness or train_num_not_passed_cases == worst_possible_fitness or test_num_not_passed_cases == worst_possible_fitness:
            generation = int(gen['Generation:'])
            genotype = eval(gen['Genotype:'])
            ind = Individual(genotype, None)
            while ind is None:
                params['MAX_TREE_DEPTH'] += 20
                ind = Individual(genotype, None)
            ind.phenotype = gen['Phenotype:']
            ind.levi_errors = None

            if test_fitness == worst_possible_fitness:
                temp_fitness_class_instance = progimpr()
                gen['Test fitness:'] = str(temp_fitness_class_instance(ind, dist='test', timeout=1000.0))
            
            if train_num_not_passed_cases == worst_possible_fitness:
                temp_fitness_file = params['FITNESS_FILE']
                temp_ind_fitness = ind.fitness
                temp_ind_levi_test_fitness = ind.levi_test_fitness
                temp_ind_levi_errors = ind.levi_errors
                
                params['FITNESS_FILE'] = 'fitness_cases.txt'
                temp_fitness_class_instance = progimpr()
                gen['Training num not passed cases:'] = str(temp_fitness_class_instance(ind, dist='training', timeout=1000.0))

                params['FITNESS_FILE'] = temp_fitness_file
                ind.fitness = temp_ind_fitness
                ind.levi_test_fitness = temp_ind_levi_test_fitness
                ind.levi_errors = temp_ind_levi_errors

            if test_num_not_passed_cases == worst_possible_fitness:
                temp_fitness_file = params['FITNESS_FILE']
                temp_ind_fitness = ind.fitness
                temp_ind_levi_test_fitness = ind.levi_test_fitness
                temp_ind_levi_errors = ind.levi_errors
                
                params['FITNESS_FILE'] = 'fitness_cases.txt'
                temp_fitness_class_instance = progimpr()
                gen['Test num not passed cases:'] = str(temp_fitness_class_instance(ind, dist='test', timeout=1000.0))

                params['FITNESS_FILE'] = temp_fitness_file
                ind.fitness = temp_ind_fitness
                ind.levi_test_fitness = temp_ind_levi_test_fitness
                ind.levi_errors = temp_ind_levi_errors
            
            s = ''
            for key in gen:
                s += key
                s += '\n'
                s += gen[key]
                s += '\n'
                s += '\n'
            
            file = create_results_folder_path(base_path=BASE_PATH, params=params, include_seed=True, make_dirs=False)
            if not file.endswith('/'):
                file += '/'
            file += str(generation) + '.txt'
            with open(file, 'w') as f:
                f.write(s)
            print(file)


if __name__ == "__main__":
    mane_post()
