import traceback
from typing import List, Any, Dict, Callable, Tuple, Optional
from multiprocessing import Process, Queue
from pandas import DataFrame
import time
import queue
import torch
import warnings
from datetime import datetime
from llmpony.llm.functions.python_code_arranger import properly_arrange_code_with_imports_functions
from llmpony.llm.testers.DatasetLoader import DatasetLoader
from llmpony.llm.models.AbstractLanguageModel import AbstractLanguageModel
from llmpony.llm.functions.json_data_io import create_and_save_json, read_json, BASE_PATH
from llmpony.llm.functions.ponyge.individual_formatter import substitute_tabs_and_newlines_with_pony_encode


class CudaOutOfMemoryWarning(Warning):
    pass


class ModelTester:
    NUM_FAILED_EXAMPLES_TO_PROMPT_WHEN_REASK: int = 10

    def __init__(
            self,
            model: AbstractLanguageModel,
            dataset_loader: DatasetLoader,
            train_size: int,
            target_train_size: int = -1,
            iterations: int = 10,
            reask: bool = False,
            repeatitions: int = 5
    ) -> None:
        if (not isinstance(model, AbstractLanguageModel)) or (model is None):
            e: str = 'You must provide an AbstractLanguageModel instance.'
            raise Exception(e)
        self.__model: AbstractLanguageModel = model
        self.__dataset_loader: DatasetLoader = dataset_loader
        self.__problems: DataFrame = self.__dataset_loader.problems
        self.__iterations: int = iterations
        self.__reask: bool = reask
        self.__iteration_timeout: int = 80
        self.__repeatitions: int = repeatitions

        self.__train_size: int = train_size
        self.__target_train_size: int = target_train_size

    def run(self, problems_indexes: Optional[List[int]] = None) -> str:
        print(f"\n{'=' * 80}")
        print(f"Model '{self.__model.name}'")
        all_problem_indexes: List[int] = list(
            range(len(self.__problems))) if problems_indexes is None else problems_indexes
        for n_prob in all_problem_indexes:
            prob_name: str = self.__problems.get('Problem Name')[n_prob].replace(' ', '-').lower()
            n_inputs: int = self.__dataset_loader.get_n_inputs(prob_name)
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            print(f'{prob_name}\n')
            start_time: float = time.time()
            responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompts=[self.__problems['Description'][n_prob]], n_inputs=n_inputs, rep_idx=None)
            _, _, data_vanilla = self.__run_all_workers_and_collect_results(responses=[res['vanilla'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=1, rep=0)
            process_timed_out_data = []
            for ddd in data_vanilla:
                if 'error' in ddd['tests_results'] and ddd['tests_results']['error'].strip() == 'Process timed out':
                    process_timed_out_data.append(ddd)
            _, _, data_preprocess = self.__run_all_workers_and_collect_results(responses=[res['preprocess'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=1, rep=0, eventual_responses_vanilla=process_timed_out_data, all_eventual_responses_vanilla=data_vanilla)
            end_time: float = time.time()
            dir_name: str = self.__create_and_save_json(data_vanilla, data_preprocess, n_prob, prob_name, (end_time - start_time) * (1 / 60))
            print(f"\nProblem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        print(f'Results saved in {dir_name}')
        print(f"{'=' * 80}")
        return dir_name

    def cached_run(self, problems_indexes: Optional[List[int]] = None) -> str:
        print(f"\n{'=' * 80}")
        print(f"Model '{self.__model.name}'")
        all_problem_indexes: List[int] = list(
            range(len(self.__problems))) if problems_indexes is None else problems_indexes
        for n_prob in all_problem_indexes:
            prob_name: str = self.__problems.get('Problem Name')[n_prob].replace(' ', '-').lower()
            n_inputs: int = self.__dataset_loader.get_n_inputs(prob_name)
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            print(f'{prob_name}\n')
            start_time: float = time.time()
            cached_results: Dict[str, Any] = read_json(
                full_path=BASE_PATH,
                model_name=self.__model.name,
                problem_benchmark=self.__dataset_loader.dataset,
                problem_benchmark_type=self.__dataset_loader.prompt_type,
                problem_id=n_prob,
                reask=False,
                iterations=self.__iterations,
                repeatitions=0,
                train_size=self.__train_size,
                test_size=self.__dataset_loader.test_size
            )
            responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompts=[self.__problems['Description'][n_prob]], n_inputs=n_inputs, rep_idx=None, cached_results=cached_results)
            _, _, data_vanilla = self.__run_all_workers_and_collect_results(responses=[res['vanilla'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=1, rep=0)
            process_timed_out_data = []
            for ddd in data_vanilla:
                if 'error' in ddd['tests_results'] and ddd['tests_results']['error'].strip() == 'Process timed out':
                    process_timed_out_data.append(ddd)
            _, _, data_preprocess = self.__run_all_workers_and_collect_results(responses=[res['preprocess'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=1, rep=0, eventual_responses_vanilla=process_timed_out_data, all_eventual_responses_vanilla=data_vanilla)
            end_time: float = time.time()
            dir_name: str = self.__create_and_save_json(data_vanilla, data_preprocess, n_prob, prob_name, (end_time - start_time) * (1 / 60))
            print(f"\nProblem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        print(f'Results saved in {dir_name}')
        print(f"{'=' * 80}")
        return dir_name

    def run_with_reask(self, problems_indexes: Optional[List[int]] = None) -> str:
        print(f"\n{'=' * 80}")
        print(f"Model '{self.__model.name}'")
        all_problem_indexes: List[int] = list(
            range(len(self.__problems))) if problems_indexes is None else problems_indexes
        for n_prob in all_problem_indexes:
            prob_name: str = self.__problems.get('Problem Name')[n_prob].replace(' ', '-').lower()
            n_inputs: int = self.__dataset_loader.get_n_inputs(prob_name)
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            print(f'{prob_name}\n')
            to_save_preprocess: List[List[Any]] = []
            to_save_vanilla: List[List[Any]] = []
            start_time: float = time.time()
            for iteration in range(self.__iterations):
                print(f'Iteration {iteration + 1}')
                data_not_passed: List[Any] = []
                previous_llm_answer: str = ''
                prompts: List[str] = []
                is_process_timed_out: bool = False
                is_syntax_error: bool = False
                for rep in range(self.__repeatitions + 1):
                    print(f'Repetition {rep}')
                    isFirst: bool = rep == 0
                    if isFirst:
                        cached_results: Optional[Dict[str, Any]] = read_json(
                            full_path=BASE_PATH,
                            model_name=self.__model.name,
                            problem_benchmark=self.__dataset_loader.dataset,
                            problem_benchmark_type=self.__dataset_loader.prompt_type,
                            problem_id=n_prob,
                            reask=False,
                            iterations=self.__iterations,
                            repeatitions=0,
                            train_size=self.__train_size,
                            test_size=self.__dataset_loader.test_size
                        )
                        prompts.append(self.__problems['Description'][n_prob])
                    else:
                        cached_results: Optional[Dict[str, Any]] = None
                        prompts.append(previous_llm_answer)
                        if is_process_timed_out:
                            prompts.append('Your code is too slow. Please, rewrite it and make it correct and more efficient. Remember to insert the necessary modules.')
                        elif is_syntax_error:
                            prompts.append('Your code contains syntax errors. Please, rewrite it and fix all the syntax errors. Remember to insert the necessary modules.')
                        else:
                            temp_prompt: List[str] = ['Your code is incorrect. Please, rewrite it. Remember to insert the necessary modules. Make sure that\n']
                            num_failed_test_cases_tot: int = len(data_not_passed[:ModelTester.NUM_FAILED_EXAMPLES_TO_PROMPT_WHEN_REASK])
                            for i in range(num_failed_test_cases_tot):
                                temp_prompt.append(
                                    str(data_not_passed[i][0])[1:-1]
                                    + ' -> '
                                    + str(data_not_passed[i][1])[1:-1]
                                    + ('\n' if i != num_failed_test_cases_tot - 1 else '')
                                )
                            prompts.append(''.join(temp_prompt))
                    try:
                        responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompts=prompts, n_inputs=n_inputs, rep_idx=f'{iteration + 1}.{rep}', cached_results=cached_results)
                    except torch.cuda.OutOfMemoryError:
                        warnings.warn(f'Warning ! torch.cuda.OutOfMemoryError encoutered for iteration {iteration} repeatition {rep} problem {n_prob}!', CudaOutOfMemoryWarning)
                        oom_data: Dict[str, Any] = {}
                        oom_data['prompt'] = self.__model.get_complete_prompt(prompts[-1], len(prompts) != 1)
                        oom_data['llm_answer'] = ''
                        oom_data['entry_point'] = 'evolve'
                        oom_data['time_minutes_llm_answer'] = 0.0
                        oom_data['no_import_syntax_errors_in_vanilla'] = False
                        oom_data['iter_id'] = f'{iteration + 1}.{rep}'
                        oom_data['iteration'] = f'{iteration}.{rep}'
                        oom_data['tests_results'] = {}
                        oom_data['problem_name'] = prob_name
                        oom_data['problem_index'] = n_prob
                        oom_data['exception'] = 'torch.cuda.OutOfMemoryError'
                        oom_data['main_func'] = '\n'.join([f'def {"evolve"}({", ".join(f"v{i}" for i in range(n_inputs))}):', '\tpass'])
                        oom_data['renamed_main_func'] = oom_data['main_func']
                        oom_data['full_code'] = '\n'.join([]) + '\n\n' + '\n\n'.join([]) + '\n\n' + oom_data['main_func'] + '\n'
                        oom_data['full_code_but_no_imports'] = oom_data['full_code']
                        to_save_preprocess.extend([oom_data])
                        to_save_vanilla.extend([oom_data])
                        break
                    previous_llm_answer = responses[0]['vanilla']['llm_answer']
                    exc, worker_res, data_vanilla = self.__run_all_workers_and_collect_results(responses=[res['vanilla'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=iteration, rep=rep)
                    process_timed_out_data = []
                    for ddd in data_vanilla:
                        if 'error' in ddd['tests_results'] and ddd['tests_results']['error'].strip() == 'Process timed out':
                            process_timed_out_data.append(ddd)        
                    _, _, data_preprocess = self.__run_all_workers_and_collect_results(responses=[res['preprocess'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=iteration, rep=rep, eventual_responses_vanilla=process_timed_out_data, all_eventual_responses_vanilla=data_vanilla)
                    to_save_preprocess.extend(data_preprocess)
                    to_save_vanilla.extend(data_vanilla)
                    is_process_timed_out = exc
                    is_syntax_error = isinstance(worker_res, str)
                    if worker_res is not None:
                        data_not_passed = worker_res[1] if (not isinstance(worker_res, str)) and isinstance(worker_res[1], list) else data_not_passed
                    if worker_res is not None and worker_res[1] == [] and not exc:
                        break
                print('\n')
            end_time: float = time.time()
            dir_name: str = self.__create_and_save_json(to_save_vanilla, to_save_preprocess, n_prob, prob_name, (end_time - start_time) * (1 / 60))
            print(f"Problem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        print(f'Results saved in {dir_name}')
        print(f"{'=' * 80}")
        return dir_name

    def __ask_model_and_process(self, prompts: List[str], n_inputs: int, rep_idx: Optional[str] = None, cached_results: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        iterations: int = 1 if self.__reask else self.__iterations
        if self.__reask:
            actual_iteration_idx: int = int(rep_idx.split('.')[0]) - 1
        else:
            actual_iteration_idx: int = -1
        responses: List[Dict[str, Any]] = []
        for iteration in range(iterations):
            if not self.__reask:
                print(f'Iteration {iteration + 1}')
            start_time_llm_answer: float = time.time()
            if cached_results is None:
                llm_answer: str = self.__model.ask(prompts)
            else:
                if self.__reask:
                    llm_answer: str = cached_results["data_vanilla"][actual_iteration_idx]['model_response']
                else:
                    llm_answer: str = cached_results["data_vanilla"][iteration]['model_response']
            end_time_llm_answer: float = time.time()
            res: Dict[str, Any] = {}
            no_import_syntax_errors_in_vanilla: bool = False
            for do_preprocessing in [False, True]:
                res_0: Dict[str, Any] = properly_arrange_code_with_imports_functions(
                    s=llm_answer,
                    include_free_code=False,
                    replace_entry_point_with_this_name='evolve',
                    replace_vars=True,
                    remove_non_existing_import=do_preprocessing,
                    n_inputs=n_inputs,
                    remove_syntax_errors=do_preprocessing
                )
                if not do_preprocessing and 'exception' not in res_0:
                    res['preprocess'] = res_0
                    res['vanilla'] = res_0
                    no_import_syntax_errors_in_vanilla = True
                    break
                res['preprocess' if do_preprocessing else 'vanilla'] = res_0
            for kk in ['preprocess', 'vanilla']:
                res[kk]['prompt'] = self.__model.get_complete_prompt(prompts[-1], len(prompts) != 1)
                res[kk]['llm_answer'] = llm_answer
                res[kk]['time_minutes_llm_answer'] = (end_time_llm_answer - start_time_llm_answer) * (1 / 60)
                res[kk]['no_import_syntax_errors_in_vanilla'] = no_import_syntax_errors_in_vanilla
                res[kk]['iter_id'] = str(iteration + 1) if rep_idx is None else rep_idx
            responses.append(res)
        return responses

    def __worker_function(self, *args_with_queue):
        result_queue = args_with_queue[-1]
        try:
            result_queue.put(self.__test_function(*args_with_queue[:-1]))
        except Exception as e:
            result_queue.put(str(e))

    def __run_all_workers_and_collect_results(self, responses: List[Dict[str, Any]], prob_name: str, n_prob: int, iteration: int, rep: int, eventual_responses_vanilla: Optional[List[Dict[str, Any]]] = None, all_eventual_responses_vanilla: Optional[List[Dict[str, Any]]] = None, evaluate_in_parallel: bool = True) -> Tuple[bool, Any, List[Dict[str, Any]]]:
        responses_copy = [res for res in responses] #if 'exception' not in res]
        f_bodies: List[str] = [res['full_code'] for res in responses_copy]
        f_names: List[str] = [res['new_entry_point'] for res in responses_copy]
        f_ind: List[int] = list(range(len(f_bodies)))
        iter_indices: List[str] = [res['iter_id'] for res in responses_copy]
        no_import_syntax_errors_in_vanillas: List[bool] = [res['no_import_syntax_errors_in_vanilla'] for res in responses_copy]
        if self.__reask:
            args: List[Tuple] = [(b, n, prob_name, iteration, Queue()) for b, n in zip(f_bodies, f_names)]
        else:
            args: List[Tuple] = [(b, n, prob_name, i, Queue()) for b, n, i in zip(f_bodies, f_names, f_ind)]
        data: List[Dict[str, Any]] = []
        for i, _ in enumerate(args):
            di = {key: responses_copy[i][key] for key in responses_copy[i]}
            di['problem_name'] = prob_name
            di['problem_index'] = n_prob
            di['iteration'] = f'{iteration}.{rep}' if self.__reask else i
            di['tests_results'] = {}
            data.append(di)
        # responses_exception = [res for res in responses if 'exception' in res]
        # for i, _ in enumerate(responses_exception):
        #     di = {key: responses_exception[i][key] for key in responses_exception[i]}
        #     di['problem_name'] = prob_name
        #     di['problem_index'] = n_prob
        #     di['iteration'] = f'{iteration}.{rep}' if self.__reask else i
        #     di['tests_results'] = {}
        #     data.append(di)
        workers = []
        print('Testing...')
        exc: bool = False
        worker_res: Any = None
        for i in range(len(args)):
            go_to_the_next = False
            curr_iter_id = iter_indices[i]
            curr_no_import_syntax_errors_in_vanilla = no_import_syntax_errors_in_vanillas[i]
            if eventual_responses_vanilla is not None:
                for ddd in eventual_responses_vanilla:
                    if curr_iter_id == ddd['iter_id']:
                        data[i]['tests_results'] = ddd['tests_results']
                        go_to_the_next = True
                        break
                if curr_no_import_syntax_errors_in_vanilla:
                    for ddd in all_eventual_responses_vanilla:
                        if curr_iter_id == ddd['iter_id']:
                            data[i]['tests_results'] = ddd['tests_results']
                            go_to_the_next = True
                            break
            if go_to_the_next:
                workers.append(None)
                continue
            if evaluate_in_parallel:
                process = Process(target=self.__worker_function, args=args[i])
                process.start()
                workers.append(process)
            else:
                workers.append(True)

        if evaluate_in_parallel:
            for i, worker in enumerate(workers):
                if worker is None:
                    continue
                try:
                    worker.join(timeout=self.__iteration_timeout)
                    if worker.is_alive():
                        worker.terminate()
                        worker.join()
                        worker.close()
                        raise Exception('Process timed out')
                    print(f'Result obtained for repetition {rep}')

                    try:
                        worker_res = args[i][-1].get(block=True, timeout=2)
                    except queue.Empty:
                        if self.__reask:
                            print(f'Exception for repetition {rep}')
                            data[i]['tests_results'] = {'passed': 0, 'error': str(e)}
                            exc = True
                        else:
                            print(f'Exception for iteration {i + 1}')
                            data[i]['tests_results'] = {'passed': 0, 'error': str(e)}
                    else:
                        if isinstance(worker_res, str):
                            data[i]['tests_results'] = {'passed': 0, 'error': worker_res}
                        else:
                            data[i]['tests_results'] = worker_res[0]
                        args[i][-1].close()

                except Exception as e:
                    if self.__reask:
                        print(f'Exception for repetition {rep}')
                        data[i]['tests_results'] = {'passed': 0, 'error': str(e)}
                        exc = True
                    else:
                        print(f'Exception for iteration {i + 1}')
                        data[i]['tests_results'] = {'passed': 0, 'error': str(e)}
        else:
            for i in range(len(args)):
                current_arg = args[i][:-1]
                current_worker = workers[i]
                if current_worker is None:
                    continue
                try:
                    seq_res = self.__test_function(*current_arg)
                except Exception as e:
                    seq_res = str(e)
                print(f'Result obtained for repetition {rep}')
                if isinstance(seq_res, str):
                    data[i]['tests_results'] = {'passed': 0, 'error': seq_res}
                else:
                    data[i]['tests_results'] = seq_res[0]
                worker_res = seq_res


        return exc, worker_res, data

    def __test_function(self, f_body: str, f_name: str, prob_name: str, n_iter: int) -> Tuple[Dict[str, int], List[Tuple[Any, Any]]]:
        train_data, test_data = self.__dataset_loader.load(prob_name, n_iter)
        
        start_time_fun_exec: float = time.time()
        
        try:
            exec(f_body, locals())
        except Exception as e:
            return str(e)
        f: Callable = eval(f_name)

        end_time_fun_exec: float = time.time()

        start_time_train_eval: float = time.time()

        X_train, y_train = train_data[0], train_data[1]
        passed: int = 0
        not_passed: int = 0
        with_exception: int = 0
        data_not_passed: List[Tuple[Any, Any]] = []
        for i in range(len(X_train)):
            try:
                result = [f(*X_train[i])]
                if result == y_train[i]:
                    passed += 1
                else:
                    not_passed += 1
                    data_not_passed.append((X_train[i], y_train[i]))
            except Exception as e:
                with_exception += 1
                data_not_passed.append((X_train[i], y_train[i]))

        end_time_train_eval: float = time.time()

        start_time_test_eval: float = time.time()

        X_test, y_test = test_data[0], test_data[1]
        passed_test: int = 0
        not_passed_test: int = 0
        with_exception_test: int = 0
        for i in range(len(X_test)):
            try:
                result = [f(*X_test[i])]
                if result == y_test[i]:
                    passed_test += 1
                else:
                    not_passed_test += 1
            except Exception as e:
                with_exception_test += 1

        end_time_test_eval: float = time.time()
        
        return {'passed': passed, 'not_passed': not_passed, 'with_exception(s)': with_exception, 'passed_test': passed_test, 'not_passed_test': not_passed_test, 'with_exception(s)_test': with_exception_test, 'time_minutes_fun_exec': (end_time_fun_exec - start_time_fun_exec) * (1 / 60), 'time_minutes_train_eval': (end_time_train_eval - start_time_train_eval) * (1 / 60), 'time_minutes_test_eval': (end_time_test_eval - start_time_test_eval) * (1 / 60)}, data_not_passed

    def __create_and_save_json(self, data_vanilla: List[Dict[str, Any]], data_preprocess: List[Dict[str, Any]], n_prob: int, prob_name: str, total_time_minutes: float) -> str:
        json_data_vanilla: List[Dict[str, Any]] = []
        json_data_preprocess: List[Dict[str, Any]] = []

        for element in data_vanilla:
            json_data_vanilla.append(self.__create_single_json_element(element))

        for element in data_preprocess:
            json_data_preprocess.append(self.__create_single_json_element(element))
        
        return create_and_save_json(
            f"{'problem'}{n_prob}",
            {
                'model_name': self.__model.name,
                'problem_benchmark': self.__dataset_loader.dataset,
                'problem_benchmark_type': self.__dataset_loader.prompt_type,
                'problem_name': prob_name,
                'n_inputs': self.__dataset_loader.get_n_inputs(prob_name),
                'problem_description': self.__problems['Description'][n_prob],
                'problem_index': n_prob,
                'data_train_size': self.__dataset_loader.train_size,
                'data_test_size': self.__dataset_loader.test_size,
                'timestamp': str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")),
                'reask': self.__reask,
                'iterations': self.__iterations,
                'repeatitions': self.__repeatitions if self.__reask else 0,
                'time_minutes_total': total_time_minutes,
                'data_vanilla': json_data_vanilla,
                'data_preprocess': json_data_preprocess
            }
        )

    def __create_single_json_element(self, element):
        json_element: Dict[str, any] = {}

        it: int = 0
        rep: int = 0
        if '.' in str(element['iteration']):
            it = int(element['iteration'].split('.')[0]) + 1
            rep = int(element['iteration'].split('.')[1])
        else:
            it = element['iteration'] + 1

        # if 'exception' in element:
        #     json_element = {
        #         'iteration': it,
        #         'repetition': rep,
        #         'model_response': element['llm_answer'],
        #         'time_minutes_model_response': element['time_minutes_llm_answer'],
        #         'iter_id': element['iter_id'],
        #         'prompt': element['prompt'],
        #         'no_import_syntax_errors_in_vanilla': element['no_import_syntax_errors_in_vanilla'],
        #         'exception': element['exception'],
        #         'tests_results': element['tests_results'] if 'tests_results' in element else {}
        #     }
        # else:
        n_inputs: int = self.__dataset_loader.get_n_inputs(element['problem_name'])
        imports: List[str] = element['imports'] if 'imports' in element else []
        sup_funcs: List[str] = element['sup_funcs'] if 'sup_funcs' in element else []        
        imports_pony: str = ''
        for i in imports:
            imports_pony += i + '#'
        used_names = element['possible_vars'] if 'possible_vars' in element else [f"v{i}" for i in range(n_inputs)]
        ind = substitute_tabs_and_newlines_with_pony_encode(element['renamed_main_func'])
        json_element = {
            'iteration': it,
            'repetition': rep,
            'model_response': element['llm_answer'],
            'time_minutes_model_response': element['time_minutes_llm_answer'],
            'iter_id': element['iter_id'],
            'prompt': element['prompt'],
            'no_import_syntax_errors_in_vanilla': element['no_import_syntax_errors_in_vanilla'],
            'function_name': element['entry_point'],
            'main_func': element['main_func'].replace(' ' + 'evolve' + '(', ' ' + element['entry_point'] + '(').replace(' (' + 'evolve' + '(', ' (' + element['entry_point'] + '(').replace(' [' + 'evolve' + '(', ' [' + element['entry_point'] + '(').replace(' {' + 'evolve' + '(', ' {' + element['entry_point'] + '('),
            'code': element['full_code'].replace(' ' + 'evolve' + '(', ' ' + element['entry_point'] + '(').replace(' (' + 'evolve' + '(', ' (' + element['entry_point'] + '(').replace(' [' + 'evolve' + '(', ' [' + element['entry_point'] + '(').replace(' {' + 'evolve' + '(', ' {' + element['entry_point'] + '('),
            'imports': imports,
            'supports': sup_funcs,
            'imports_and_supports': element['imports_and_supports'] if 'imports_and_supports' in element else '\n'.join(imports) + '\n\n' + '\n\n'.join(sup_funcs) + '\n',
            'variables_names': used_names,
            'renamed_main_func': element['renamed_main_func'],
            'final_individual': ind,
            'tests_results': element['tests_results'] if 'tests_results' in element else {}
        }
        
        if 'exception' in element:
            json_element['exception'] = element['exception']
        
        return json_element
    
