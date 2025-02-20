import json
import os
import queue
from multiprocessing import Queue, Process

BASE_PATH: str = "../llm_results/"
ALREADY_SOLVED_STRING: str = 'ALREADY_SOLVED'
NOT_PARSED_STRING: str = 'NOT_PARSED'


# ======================================================================================
# SUPPORT FUNCTION
# ======================================================================================


def create_dir_path_string(
    full_path: str,
    model_name: str,
    problem_benchmark: str,
    problem_benchmark_type: str,
    problem_id: int,
    reask: bool,
    iterations: int,
    repeatitions: int,
    train_size: int,
    test_size: int
) -> str:
    if full_path is None or (full_path is not None and full_path.strip() == ''):
        full_path = BASE_PATH
    
    if reask:
        full_path += 'LPLUS' + '/'
    else:
        full_path += 'L' + '/'
    
    full_path += problem_benchmark + '_' + problem_benchmark_type + '/'
    full_path += model_name + '/'

    if reask:
        full_path += 'iter' + str(iterations) + '_rep' + str(repeatitions) + '/'
    else:
        full_path += 'iter' + str(iterations) + '_rep0' + '/'

    full_path += f'train{train_size}_test{test_size}' + '/'

    results_folder_path: str = full_path
    output_file_path: str = os.path.join(results_folder_path, f"{'problem'}{problem_id}{'.json'}")
    
    return output_file_path


def read_json(
    full_path: str,
    model_name: str,
    problem_benchmark: str,
    problem_benchmark_type: str,
    problem_id: int,
    reask: bool,
    iterations: int,
    repeatitions: int,
    train_size: int,
    test_size: int
) -> dict[str, any]:
    
    output_file_path: str = create_dir_path_string(
        full_path=full_path,
        model_name=model_name,
        problem_benchmark=problem_benchmark,
        problem_benchmark_type=problem_benchmark_type,
        problem_id=problem_id,
        reask=reask,
        iterations=iterations,
        repeatitions=repeatitions,
        train_size=train_size,
        test_size=test_size
    )
    
    with open(output_file_path, 'r') as f:
        d: dict[str, any] = json.load(f)
    
    return d





# ======================================================================================
# EVALUATE TEST CASES
# ======================================================================================

def exec_single_evaluate(*args):
    program = args[0]
    queue_t = args[1]
    try:
        exec(program, locals())
        queue_t.put(True)
    except:
        queue_t.put(False)


def evaluate(idx: int, all_solutions: list[str], all_function_names: list[str]) -> list[bool]:
    if len(all_solutions) != len(all_function_names):
        raise AttributeError(f'The length of solutions list ({len(all_solutions)}) is different from the length of function names list ({len(all_function_names)}).')
    
    with open('humaneval.json', 'r') as f:
        data = json.load(f)

    he = data[idx]
    outcomes: list[bool] = []
    for solution, function_name in zip(all_solutions, all_function_names):

        correct_code: str = solution + '\n\n'
        correct_code += he['test'] + '\n\n'
        correct_code += f'check({function_name})' + '\n\n'
    
        args = (correct_code, Queue())
        worker = Process(target=exec_single_evaluate, args=args)
        worker.start()
        try:
            worker.join(timeout=10)
            if worker.is_alive():
                worker.terminate()
                worker.join()
                worker.close()
                raise Exception('Process timed out')
            
            try:
                current_outcome = args[1].get(block=True, timeout=2)
            except queue.Empty:
                outcomes.append(False)
            else:
                outcomes.append(current_outcome)
                args[1].close()
        except Exception:
            outcomes.append(False)

    return outcomes


def evaluate_all(solutions_for_each_problem: list[list[str]], function_names_for_each_problem: list[list[str]], threshold: int) -> int:
    if len(solutions_for_each_problem) != 164:
        raise AttributeError(f'Missing problems of humaneval for the solutions list, found {len(solutions_for_each_problem)}.')
    if len(function_names_for_each_problem) != 164:
        raise AttributeError(f'Missing problems of humaneval for the function names list, found {len(function_names_for_each_problem)}.')
    if threshold <= 0:
        raise AttributeError(f'Threshold must be at least one, found {threshold}.')

    n_solved_problems: int = 0
    for idx in range(164):
        all_solutions: list[str] = solutions_for_each_problem[idx]
        all_function_names: list[str] = function_names_for_each_problem[idx]
        outcomes: list[bool] = evaluate(idx=idx, all_solutions=all_solutions, all_function_names=all_function_names)
        n_correct_solutions: int = sum([int(outc) for outc in outcomes])
        if n_correct_solutions >= threshold:
            n_solved_problems += 1

    return n_solved_problems


def main():
    model_names: list[str] = ["Gemma2B", "CodeGemma7B", "CodeLLaMA7B", "LLaMA318B", "LLaMA323B", "Mistral7B", "Phi35Mini"]
    dataset_sizes: list[tuple[int, int]] = [(20, 1000)]
    data: dict[str, dict[str, list[list[str]]]] = {model_name + '_' + str(train_size) + '_' + str(test_size): {'solutions_for_each_problem': [], 'function_names_for_each_problem': []} for model_name in model_names for train_size, test_size in dataset_sizes}
    for model_name in model_names:
        for train_size, test_size in dataset_sizes:
            for problem_id in list(range(0, 163 + 1)):
                d = read_json(
                        full_path=BASE_PATH,
                        model_name=model_name,
                        problem_benchmark='humaneval',
                        problem_benchmark_type='text',
                        problem_id=problem_id,
                        reask=False,
                        iterations=10,
                        repeatitions=0,
                        train_size=train_size,
                        test_size=test_size
                    )
                
                solutions_0: list[str] = []
                function_names_0: list[str] = []
                for dd in d["data_vanilla"]:
                    if "code" in dd and "function_name" in dd:
                        solutions_0.append(dd["code"])
                        function_names_0.append(dd["function_name"])
                    else:
                        solutions_0.append("def evolve(v0):\n\tpass")
                        function_names_0.append("evolve")
                data[model_name + '_' + str(train_size) + '_' + str(test_size)]["solutions_for_each_problem"].append(solutions_0)
                data[model_name + '_' + str(train_size) + '_' + str(test_size)]["function_names_for_each_problem"].append(function_names_0)
    
    for threshold in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        print("THRESHOLD " + str(threshold))
        print()
        print()
        for train_size, test_size in dataset_sizes:
            print("TRAIN SIZE " + str(train_size))
            print()
            for model_name in model_names:
                n_solved_problems: int = evaluate_all(data[model_name + '_' + str(train_size) + '_' + str(test_size)]["solutions_for_each_problem"], data[model_name + '_' + str(train_size) + '_' + str(test_size)]["function_names_for_each_problem"], threshold)
                print("{:<20s} {:<10s} {:<10s}".format(model_name, " : ", str(round(n_solved_problems / 164, 2))))
            print()


if __name__ == '__main__':
    main()
