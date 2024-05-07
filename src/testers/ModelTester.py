from typing import List, Any, Dict, Callable, Tuple, Optional
from multiprocessing import Process, Queue
from pandas import DataFrame
from scripts.python_code_arranger import properly_arrange_code_with_imports_functions
from testers.DatasetLoader import DatasetLoader
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_and_save_json, get_results_dir_path
from scripts.ponyge.individual_formatter import substitute_tabs_and_newlines_with_pony_encode


class ModelTester():
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
        self.__iteration_timeout: int = 60
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
            responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompt=self.__problems['Description'][n_prob], n_inputs=n_inputs, isFirst=None)
            _, _, data = self.__run_all_workers_and_collect_results(responses=responses, prob_name=prob_name, n_prob=n_prob, iteration=1, rep=1)
            self.__create_and_save_json(data, n_prob, prob_name)
            print(f"\nProblem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        dir_name: str = get_results_dir_path()
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
            to_save: List[List[Any]] = []
            for iteration in range(self.__iterations):
                print(f'Iteration {iteration + 1}')
                data_not_passed: List[Any] = []
                for rep in range(self.__repeatitions):
                    print(f'Repetition {rep + 1}')
                    prompt: str = ''
                    if data_not_passed == []:
                        prompt = self.__problems['Description'][n_prob]
                    else:
                        if data_not_passed != []:
                            temp_prompt: List[str] = ['Make sure that\n']
                            for i in range(len(data_not_passed[:20])):
                                temp_prompt.append(
                                    str(data_not_passed[i][0])
                                    .replace('[', '')
                                    .replace(']', '')
                                    + ' -> '
                                    + str(data_not_passed[i][1])
                                    .replace('[', '')
                                    .replace(']', '')
                                    + '\n'
                                )
                            prompt = ''.join(temp_prompt)
                    isFirst: bool = True if rep == 0 else False
                    responses: List[Dict[str, Any]] = self.__ask_model_and_process(prompt=prompt, n_inputs=n_inputs, isFirst=isFirst)
                    exc, worker_res, data = self.__run_all_workers_and_collect_results(responses=responses, prob_name=prob_name, n_prob=n_prob, iteration=iteration, rep=rep)
                    to_save.extend(data)
                    if worker_res[1] == [] and not exc:
                        break
                print('\n')
            self.__create_and_save_json(to_save, n_prob, prob_name)
            print(f"Problem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        dir_name: str = get_results_dir_path()
        print(f'Results saved in {dir_name}')
        print(f"{'=' * 80}")
        return dir_name

    def __ask_model_and_process(self, prompt: str, n_inputs: int, isFirst: Optional[bool] = None) -> List[Dict[str, Any]]:
        iterations: int = 1 if self.__reask else self.__iterations
        responses: List[Dict[str, Any]] = []
        reask: bool = self.__reask
        if isFirst:
            reask = False
        for iteration in range(iterations):
            if not self.__reask:
                print(f'Iteration {iteration + 1}')
            llm_answer: str = self.__model.ask(prompt, reask)
            res: Dict[str, Any] = properly_arrange_code_with_imports_functions(
                s=llm_answer,
                include_free_code=False,
                replace_entry_point_with_this_name='evolve',
                replace_vars=True,
                remove_non_existing_import=False,
                n_inputs=n_inputs,
                remove_syntax_errors=False
            )
            res['llm_answer'] = llm_answer
            responses.append(res)
        return responses

    def __worker_function(self, *args_with_queue):
        result_queue = args_with_queue[-1]
        try:
            result_queue.put(self.__test_function(*args_with_queue[:-1]))
        except Exception as e:
            result_queue.put(str(e))

    def __run_all_workers_and_collect_results(self, responses: List[Dict[str, Any]], prob_name: str, n_prob: int, iteration: int, rep: int) -> Tuple[bool, Any, List[Dict[str, Any]]]:
        f_bodies: List[str] = [res['full_code'] for res in responses]
        f_names: List[str] = [res['new_entry_point'] for res in responses]
        args: List[Tuple] = [(b, n, prob_name, Queue()) for b, n in zip(f_bodies, f_names)]
        data: List[Dict[str, Any]] = []
        for i, _ in enumerate(args):
            di = {key: responses[i][key] for key in responses[i]}
            di['problem_name'] = prob_name
            di['problem_index'] = n_prob
            di['iteration'] = f'{iteration}.{rep}' if self.__reask else i
            data.append(di)
        workers = []
        print('Testing...')
        for i in range(len(args)):
            process = Process(target=self.__worker_function, args=args[i])
            process.start()
            workers.append(process)
        for i, worker in enumerate(workers):
            exc: bool = False
            try:
                worker.join(timeout=self.__iteration_timeout)
                if worker.is_alive():
                    worker.terminate()
                    raise Exception('Process timed out')
                print(f'Result obtained for repetition {rep + 1}')
                worker_res = args[i][-1].get()
                if isinstance(worker_res, str):
                    data[i]['test_results'] = {'passed': 0, 'error': worker_res}
                else:
                    data[i]['test_results'] = worker_res[0]
            except Exception as e:
                if self.__reask:
                    print(f'Exception for repetition {rep + 1}')
                    data[i]['test_results'] = {'passed': 0, 'error': str(e)}
                    exc = True
                else:
                    print(f'Exception for iteration {i + 1}')
                    data[i]['test_results'] = {'passed': 0, 'error': str(e)}
        return exc, worker_res, data

    def __test_function(self, f_body: str, f_name: str, prob_name: str) -> Tuple[Dict[str, int], List[Tuple[Any, Any]]]:
        try:
            exec(f_body, locals())
        except Exception as e:
            return str(e)
        f: Callable = eval(f_name)
        train_data, test_data = self.__dataset_loader.load(prob_name)

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

        return {'passed': passed, 'not_passed': not_passed, 'with_exception(s)': with_exception, 'passed_test': passed_test, 'not_passed_test': not_passed_test, 'with_exception(s)_test': with_exception_test}, data_not_passed

    def __create_and_save_json(self, data: List[Dict[str, Any]], n_prob: int, prob_name: str) -> None:
        json_data: List[Dict[str, Any]] = []
        json_element: Dict[str, any] = {}

        for element in data:
            imports: List[str] = element['imports']
            imports_pony: str = ''
            for i in imports:
                imports_pony += i + '#'
            used_names = element['possible_vars']
            ind = imports_pony + substitute_tabs_and_newlines_with_pony_encode(element['renamed_main_func'])  # imports_pony ??
            it: int = 0
            rep: int = 0
            if '.' in str(element['iteration']):
                it = int(element['iteration'].split('.')[0]) + 1
                rep = int(element['iteration'].split('.')[1]) + 1
            else:
                it = element['iteration'] + 1
                rep = 1
            json_element = {
                'iteration': it,
                'repetition': rep,
                'model_response': element['llm_answer'],
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
            json_data.append(json_element)
        create_and_save_json(
            f"{self.__model.name}{'_problem'}{n_prob}",
            {
                'model_name': self.__model.name,
                'problem_benchmark': self.__dataset_loader.dataset,
                'problem_name': prob_name,
                'n_inputs': self.__dataset_loader.get_n_inputs(prob_name),
                'prompt': self.__problems['Description'][n_prob],
                'problem_index': n_prob,
                'data_train_size': self.__dataset_loader.train_size,
                'data_test_size': self.__dataset_loader.test_size,
                'data': json_data
            }
        )
