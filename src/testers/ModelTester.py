from typing import List, Any, Dict, Callable, Tuple
from multiprocessing import Process, Queue
from pandas import DataFrame
from scripts.python_code_arranger import properly_arrange_code_with_imports_functions_globals
from testers.DatasetLoader import DatasetLoader
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_and_save_json, get_results_dir_path
from scripts.ponyge.individual_formatter import (substitute_tabs_and_newlines_with_pony_encode,
                                                 replace_variables_with_names)


class ModelTester():
    def __init__(
            self,
            model: AbstractLanguageModel,
            dataset_loader: DatasetLoader,
            iterations: int = 5,
            reask: bool = False
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

    def run(self) -> str:
        print(f'\n{'=' * 80}')
        print(f"Model '{self.__model.name}'")
        for n_prob in range(len(self.__problems)):
            print(f'{'=' * 35}Problem {(n_prob):02d}{'=' * 35}')
            res: Dict[str, List[str]] = self.__ask_model_and_process(self.__problems['Description'][n_prob])
            prob_name: str = self.__problems.get('Problem Name')[n_prob].replace(' ', '-').lower()
            # Body, Name, ProbName, Queue
            args: List[Tuple] = self.__create_task_input(prob_name, res['code'], res['f_names'])
            data: List[Dict[str, Any]] = []
            for i, arg in enumerate(args):
                di = {}
                di['f_body'] = arg[0]
                di['f_name'] = arg[1]
                di['problem_name'] = arg[2]
                di['problem_index'] = i
                di['f_mains'] = res['f_mains'][i]
                di['responses'] = res['responses'][i]
                di['imports'] = res['imports'][i]
                data.append(di)
            workers = []
            print('\nTesting...')
            for i in range(len(args)):
                process = Process(target=self.__worker_function, args=args[i])
                process.start()
                workers.append(process)
            for i, worker in enumerate(workers):
                try:
                    worker.join(timeout=self.__iteration_timeout)
                    if worker.is_alive():
                        worker.terminate()
                        raise Exception('Process timed out')
                    print(f'Result obtained for iteration {i + 1}')
                    task_res, _ = args[i][-1].get()
                    if isinstance(task_res, Exception):
                        data[i]['test_results'] = {'passed': 0, 'error': str(task_res)}
                    else:
                        data[i]['test_results'] = task_res
                except Exception as e:
                    print(f'Exception for iteration {i + 1}')
                    data[i]['test_results'] = {'passed': 0, 'error': str(e)}
            self.__create_and_save_json(data, n_prob, prob_name)
            print(f"\nProblem '{prob_name}' completed.")
            print(f'{'=' * 80}')
        dir_name: str = get_results_dir_path()
        print(f'Results saved in {dir_name}')
        print(f'{'=' * 80}')
        return dir_name

    def run_with_reask(self) -> str:
        print(f'\n{'=' * 80}')
        print(f"Model '{self.__model.name}'")
        for n_prob in range(len(self.__problems)):
            print(f'{'=' * 35}Problem {(n_prob):02d}{'=' * 35}')
            to_save: List[List[Any]] = []
            for iteration in range(self.__iterations):
                print(f'Iteration {iteration + 1}')
                data_not_passed: List[Any] = []
                for rep in range(5):
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
                    res: Dict[str, List[str]] = self.__ask_model_and_process(prompt, isFirst)
                    prob_name: str = (
                        self.__problems.get('Problem Name')[n_prob]
                        .replace(' ', '-')
                        .lower()
                    )
                    args: List[Tuple] = self.__create_task_input(
                        prob_name, res['code'], res['f_names']
                    )
                    data: List[List[Any]] = []
                    for i, arg in enumerate(args):
                        temp = list(arg)
                        temp.pop()
                        temp.append(res['responses'][i])
                        temp.append(res['imports'][i])
                        temp.append(f'{iteration}.{rep}')
                        data.append(temp)
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
                            task_res, data_not_passed = args[i][-1].get()
                            if isinstance(task_res, Exception):
                                data[i].append({'passed': 0, 'error': str(task_res)})
                            else:
                                data[i].append(task_res)
                        except Exception as e:
                            print(f'Exception for repetition {rep + 1}')
                            data[i].append({'passed': 0, 'error': str(e)})
                            exc = True
                    to_save.extend(data)
                    if data_not_passed == [] and not exc:
                        break
                print('\n')
            self.__create_and_save_json(to_save, n_prob, prob_name)
            print(f"Problem '{prob_name}' completed.")
            print(f'{'=' * 80}')
        dir_name: str = get_results_dir_path()
        print(f'Results saved in {dir_name}')
        print(f'{'=' * 80}')
        return dir_name

    def __ask_model_and_process(self, prompt: str, isFirst=None) -> Dict[str, Any]:
        iterations: int = 1 if self.__reask else self.__iterations
        responses: List[str] = []
        code: List[str] = []
        f_imports: List[List[str]] = []
        f_names: List[str] = []
        f_mains: List[str] = []
        reask: bool = True if self.__reask else False
        if isFirst:
            reask = False
        for iteration in range(iterations):
            if not self.__reask:
                print(f'Iteration {iteration + 1}')
            responses.append(self.__model.ask(prompt, reask))
            formatted_code, entry_point, all_imports, main_func = properly_arrange_code_with_imports_functions_globals(responses[-1], False)
            code.append(formatted_code)
            f_names.append(entry_point)
            f_imports.append(all_imports)
            f_mains.append(main_func)
        return {
            'responses': responses,
            'code': code,
            'imports': f_imports,
            'f_names': f_names,
            'f_mains': f_mains
        }

    def __create_task_input(self, prob_name: str, f_bodies: List[str], f_names: List[str]) -> List[Tuple]:
        return [(b, n, prob_name, Queue()) for b, n in zip(f_bodies, f_names)]

    def __worker_function(self, *args_with_queue):
        result_queue = args_with_queue[-1]
        try:
            result_queue.put(self.__test_function(*args_with_queue[:-1]))
        except Exception as e:
            result_queue.put(e)

    def __test_function(self, f_body: str, f_name: str, prob_name: str) -> Tuple[Dict[str, int], List[Tuple[Any, Any]]]:
        try:
            exec(f_body, locals())
        except Exception as e:
            raise Exception('Cannot define function') from e
        else:
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
            imports: List[str] = list(set(e.strip() for e in element['imports']))
            imports_pony: str = ''
            for i in imports:
                imports_pony += i + '#'
            ind: str = imports_pony + substitute_tabs_and_newlines_with_pony_encode(element['f_mains']) # Pass main_func
            _, used_names = replace_variables_with_names('\n'.join(element['imports']) + '\n' + element['f_mains'], imports)
            it: int = 0
            rep: int = 0
            if '.' in str(element['problem_index']):
                it = int(element['problem_index'].split('.')[0]) + 1
                rep = int(element['problem_index'].split('.')[1]) + 1
            else:
                it = element['problem_index'] + 1
                rep = 1
            json_element = {
                'iteration': it,
                'repetition': rep,
                'model_response': element['responses'],
                'imports': imports,
                'variables_names': used_names,
                'function_name': element['f_name'],
                'code': element['f_body'],
                'final_individual': ind.replace(element['f_name'] + '(', 'evolve('),
                'tests_results': element['test_results']
            }
            json_data.append(json_element)
        create_and_save_json(
            f'{self.__model.name}{'_problem'}{n_prob}',
            {
                'model_name': self.__model.name,
                'problem_name': prob_name,
                'prompt': self.__problems['Description'][n_prob],
                'problem_index': n_prob,
                'data_train_size': self.__dataset_loader.train_size,
                'data': json_data
            }
        )
