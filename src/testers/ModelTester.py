import traceback
from typing import List, Any, Dict, Callable, Tuple, Optional
from multiprocessing import Process, Queue
from pandas import DataFrame
import time
from datetime import datetime
from scripts.python_code_arranger import properly_arrange_code_with_imports_functions
from testers.DatasetLoader import DatasetLoader
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_io import create_and_save_json
from scripts.ponyge.individual_formatter import substitute_tabs_and_newlines_with_pony_encode


class ModelTester():
    NUM_FAILED_EXAMPLES_TO_PROMPT_WHEN_REASK: int = 20

    def __init__(
            self,
            model: AbstractLanguageModel,
            dataset_loader: DatasetLoader,
            iterations: int = 5,
            reask: bool = False,
            repeatitions: int = 10
    ) -> None:
        if (not isinstance(model, AbstractLanguageModel)) or (model == None):
            e: str = 'You must provide an AbstractLanguageModel instance.'
            raise Exception(e)
        self.__model: AbstractLanguageModel = model
        self.__dataset_loader: DatasetLoader = dataset_loader
        self.__problems: DataFrame = self.__dataset_loader.problems
        self.__iterations: int = iterations
        self.__reask: bool = reask
        self.__iteration_timeout: int = 120
        self.__repeatitions: int = repeatitions

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
            responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompt=self.__problems['Description'][n_prob], n_inputs=n_inputs, isFirst=None, rep_idx=None)
            _, _, data_vanilla = self.__run_all_workers_and_collect_results(responses=[res['vanilla'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=1, rep=0)
            process_timed_out_data = []
            for ddd in data_vanilla:
                if 'error' in ddd['test_results'] and ddd['test_results']['error'].strip() == 'Process timed out':
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
                for rep in range(self.__repeatitions + 1):
                    print(f'Repetition {rep}')
                    isFirst: bool = rep == 0
                    prompt: str = '' if isFirst else 'Your code is incorrect. Please, rewrite it.\n'
                    if data_not_passed == []:
                        prompt += self.__problems['Description'][n_prob]
                    else:
                        temp_prompt: List[str] = ['Make sure that\n']
                        for i in range(len(data_not_passed[:ModelTester.NUM_FAILED_EXAMPLES_TO_PROMPT_WHEN_REASK])):
                            temp_prompt.append(
                                str(data_not_passed[i][0])[1:-1]
                                + ' -> '
                                + str(data_not_passed[i][1])[1:-1]
                                + '\n'
                            )
                        prompt += ''.join(temp_prompt)
                    responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompt=prompt, n_inputs=n_inputs, isFirst=isFirst, rep_idx=f'{iteration}.{rep}')
                    exc, worker_res, data_vanilla = self.__run_all_workers_and_collect_results(responses=[res['vanilla'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=iteration, rep=rep)
                    process_timed_out_data = []
                    for ddd in data_vanilla:
                        if 'error' in ddd['test_results'] and ddd['test_results']['error'].strip() == 'Process timed out':
                            process_timed_out_data.append(ddd)        
                    _, _, data_preprocess = self.__run_all_workers_and_collect_results(responses=[res['preprocess'] for res in responses], prob_name=prob_name, n_prob=n_prob, iteration=iteration, rep=rep, eventual_responses_vanilla=process_timed_out_data, all_eventual_responses_vanilla=data_vanilla)
                    to_save_preprocess.extend(data_preprocess)
                    to_save_vanilla.extend(data_vanilla)
                    if worker_res is not None:
                        data_not_passed = worker_res[1]
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

    def __ask_model_and_process(self, prompt: str, n_inputs: int, isFirst: Optional[bool] = None, rep_idx: Optional[str] = None) -> List[Dict[str, Any]]:
        iterations: int = 1 if self.__reask else self.__iterations
        responses: List[Dict[str, Any]] = []
        reask: bool = self.__reask
        if isFirst:
            reask = False
        for iteration in range(iterations):
            if not self.__reask:
                print(f'Iteration {iteration + 1}')
            start_time_llm_answer: float = time.time()
            llm_answer: str = self.__model.ask(prompt, reask)
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
                res[kk]['prompt'] = self.__model.get_complete_prompt(prompt, reask)
                res[kk]['llm_answer'] = llm_answer
                res[kk]['time_minutes_llm_answer'] = (end_time_llm_answer - start_time_llm_answer) * (1 / 60)
                res[kk]['no_import_syntax_errors_in_vanilla'] = no_import_syntax_errors_in_vanilla
                res[kk]['iter_id'] = str(iteration) if rep_idx is None else rep_idx
            responses.append(res)
        return responses

    def __worker_function(self, *args_with_queue):
        result_queue = args_with_queue[-1]
        try:
            result_queue.put(self.__test_function(*args_with_queue[:-1]))
        except Exception as e:
            result_queue.put(str(e))

    def __run_all_workers_and_collect_results(self, responses: List[Dict[str, Any]], prob_name: str, n_prob: int, iteration: int, rep: int, eventual_responses_vanilla: Optional[List[Dict[str, Any]]] = None, all_eventual_responses_vanilla: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, Any, List[Dict[str, Any]]]:
        responses_copy = [res for res in responses if 'exception' not in res]
        f_bodies: List[str] = [res['full_code'] for res in responses_copy]
        f_names: List[str] = [res['new_entry_point'] for res in responses_copy]
        iter_indices: List[str] = [res['iter_id'] for res in responses_copy]
        no_import_syntax_errors_in_vanillas: List[bool] = [res['no_import_syntax_errors_in_vanilla'] for res in responses_copy]
        args: List[Tuple] = [(b, n, prob_name, Queue()) for b, n in zip(f_bodies, f_names)]
        data: List[Dict[str, Any]] = []
        for i, _ in enumerate(args):
            di = {key: responses_copy[i][key] for key in responses_copy[i]}
            di['problem_name'] = prob_name
            di['problem_index'] = n_prob
            di['iteration'] = f'{iteration}.{rep}' if self.__reask else i
            di['test_results'] = {}
            data.append(di)
        responses_exception = [res for res in responses if 'exception' in res]
        for i, _ in enumerate(responses_exception):
            di = {key: responses_exception[i][key] for key in responses_exception[i]}
            di['problem_name'] = prob_name
            di['problem_index'] = n_prob
            di['iteration'] = f'{iteration}.{rep}' if self.__reask else i
            di['test_results'] = {}
            data.append(di)
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
                        data[i]['test_results'] = ddd['test_results']
                        go_to_the_next = True
                        break
                if curr_no_import_syntax_errors_in_vanilla:
                    for ddd in all_eventual_responses_vanilla:
                        if curr_iter_id == ddd['iter_id']:
                            data[i]['test_results'] = ddd['test_results']
                            go_to_the_next = True
                            break
            if go_to_the_next:
                workers.append(None)
                continue
            process = Process(target=self.__worker_function, args=args[i])
            process.start()
            workers.append(process)
        for i, worker in enumerate(workers):
            if worker is None:
                continue
            try:
                worker.join(timeout=self.__iteration_timeout)
                if worker.is_alive():
                    worker.terminate()
                    raise Exception('Process timed out')
                print(f'Result obtained for repetition {rep}')
                worker_res = args[i][-1].get()
                if isinstance(worker_res, str):
                    data[i]['test_results'] = {'passed': 0, 'error': worker_res}
                else:
                    data[i]['test_results'] = worker_res[0]
            except Exception as e:
                if self.__reask:
                    print(f'Exception for repetition {rep}')
                    data[i]['test_results'] = {'passed': 0, 'error': str(e)}
                    exc = True
                else:
                    print(f'Exception for iteration {i + 1}')
                    data[i]['test_results'] = {'passed': 0, 'error': str(e)}
        return exc, worker_res, data

    def __test_function(self, f_body: str, f_name: str, prob_name: str) -> Tuple[Dict[str, int], List[Tuple[Any, Any]]]:
        train_data, test_data = self.__dataset_loader.load(prob_name)
        
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

        if 'exception' in element:
            json_element = {
                'iteration': it,
                'repetition': rep,
                'model_response': element['llm_answer'],
                'time_minutes_model_response': element['time_minutes_llm_answer'],
                'iter_id': element['iter_id'],
                'prompt': element['prompt'],
                'no_import_syntax_errors_in_vanilla': element['no_import_syntax_errors_in_vanilla'],
                'exception': element['exception'],
                'tests_results': element['test_results'] if 'test_results' in element else {}
            }
        else:
            imports: List[str] = element['imports']
            imports_pony: str = ''
            for i in imports:
                imports_pony += i + '#'
            used_names = element['possible_vars']
            ind = imports_pony + substitute_tabs_and_newlines_with_pony_encode(element['renamed_main_func'])  # imports_pony ??
            json_element = {
                'iteration': it,
                'repetition': rep,
                'model_response': element['llm_answer'],
                'time_minutes_model_response': element['time_minutes_llm_answer'],
                'iter_id': element['iter_id'],
                'prompt': element['prompt'],
                'no_import_syntax_errors_in_vanilla': element['no_import_syntax_errors_in_vanilla'],
                'function_name': element['entry_point'],
                'main_func': element['main_func'].replace('evolve' + '(', element['entry_point'] + '('),
                'code': element['full_code'].replace('evolve' + '(', element['entry_point'] + '('),
                'imports': imports,
                'supports': element['sup_funcs'],
                'imports_and_supports': element['imports_and_supports'],
                'variables_names': used_names,
                'final_individual': ind,
                'tests_results': element['test_results']
            }
        
        return json_element
    