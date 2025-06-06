import json

from llmpony.pony.utilities.stats.file_io import BASE_PATH, create_results_folder_path, read_ponyge_results
import os


def fix():
    new_base_path = '../NEW_FILES/'
    all_seeds = list(range(10))
    benchmarks = [('psb2', 'text', list(range(25))), ('humaneval', 'text', list(range(164)))]
    models = ['Mistral7B', 'Gemma2B', 'CodeGemma7B', 'CodeLLaMA7B', 'LLaMA318B', 'LLaMA323B', 'Phi35Mini']
    bnf_type = 'dynamicbnf'
    fitness_function = 'progimpr'
    fitness_file = 'fitness_type_lexi.txt'
    all_num_train_examples = [20, 40, 60]
    num_test_examples = 1000
    selections = ['tournament', 'lexicase']
    tournament_size = 5
    crossover = 'subtree'
    mutation = 'subtree'
    population_size = 200
    generations = 100
    crossover_probability = 0.8
    mutation_probability = 0.6
    for benchmark_name, benchmark_type, all_problem_indexes in benchmarks:
        print(f'{benchmark_name} {benchmark_type}')
        for model_name in models:
            print(model_name)
            for num_train_examples in all_num_train_examples:
                print(num_train_examples)
                for problem_index in all_problem_indexes:
                    for selection in selections:
                        for random_seed in all_seeds:
                            params = {
                                    'BENCHMARK_NAME': benchmark_name,
                                    'BENCHMARK_TYPE': benchmark_type,
                                    'BNF_TYPE': bnf_type,
                                    'MODEL_NAME': model_name,
                                    'FITNESS_FUNCTION': fitness_function,
                                    'FITNESS_FILE': fitness_file,
                                    'NUM_TRAIN_EXAMPLES': num_train_examples,
                                    'NUM_TEST_EXAMPLES': num_test_examples,
                                    'SELECTION': selection,
                                    'TOURNAMENT_SIZE': tournament_size,
                                    'SELECTION_SAMPLE_SIZE': num_train_examples,
                                    'CROSSOVER': crossover,
                                    'MUTATION': mutation,
                                    'POPULATION_SIZE': population_size,
                                    'GENERATIONS': generations,
                                    'CROSSOVER_PROBABILITY': crossover_probability,
                                    'MUTATION_PROBABILITY': mutation_probability,
                                    'PROBLEM_INDEX': problem_index,
                                    'RANDOM_SEED': random_seed
                            }
                            try:
                                res = read_ponyge_results(BASE_PATH, params, include_seed=True)
                            except:
                                continue                        
                            stats = res['stats']
                            del stats['Unnamed: 61']
                            gens = res['gens']

                            old_path = create_results_folder_path(BASE_PATH, params, True, False)
                            new_path = create_results_folder_path(new_base_path, params, True, True)

                            stats.to_csv(os.path.join(new_path, 'stats.csv'), sep='\t', header=True, index=False)

                            with open(os.path.join(old_path, 'parameters.txt'), 'r') as f:
                                parameter_file_content = f.read()

                            with open(os.path.join(new_path, 'parameters.txt'), 'w') as f:
                                f.write(parameter_file_content)

                            new_gens = []
                            for single_gen in gens:
                                new_gens.append({key.replace('\n', '').replace(':', ''): single_gen[key] for key in single_gen if key != 'Execution time (min):'})

                            new_gens = {'gens': new_gens}

                            with open(os.path.join(new_path, 'bests.json'), 'w') as f:
                                json.dump(new_gens, f, indent=4)


if __name__ == '__main__':
    fix()
