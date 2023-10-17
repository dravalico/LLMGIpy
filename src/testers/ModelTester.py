from typing import List, Any, Dict, Callable, Tuple
from multiprocessing import Process, Queue
from pandas import DataFrame
from testers.DatasetLoader import DatasetLoader
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_and_save_json, get_results_dir_path
from scripts.function_util import (extract_external_imports,
                                   extract_function,
                                   extract_function_name,
                                   tabs_as_symbol,
                                   extract_internal_imports,
                                   remove_imports_and_comments_and_format_tabs,
                                   insert_strings_after_signature)
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
            e: str = "You must provide an AbstractLanguageModel instance."
            raise Exception(e)
        self.__model: AbstractLanguageModel = model
        self.__dataset_loader: DatasetLoader = dataset_loader
        self.__problems: DataFrame = self.__dataset_loader.problems
        self.__iterations: int = iterations
        self.__reask: bool = reask
        self.__iteration_timeout: int = 60

    def run(self) -> str:
        print(f"\n{'=' * 80}")
        print(f"Model '{self.__model.name}'")
        for n_prob in range(len(self.__problems)):
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            res: Dict[str, List[str]] = self.__ask_model_and_process(self.__problems["Description"][n_prob])
            prob_name: str = self.__problems\
                .get("Problem Name")[n_prob]\
                .replace(' ', '-')\
                .lower()
            args: List[Tuple] = self.__create_task_input(prob_name, res["code"], res["f_names"])
            data: List[List[Any]] = []
            for i, arg in enumerate(args):
                temp = list(arg)
                temp.pop()
                temp.append(res["responses"][i])
                temp.append(res["imports"][i])
                temp.append(i)
                data.append(temp)
            workers = []
            print("\nTesting...")
            for i in range(len(args)):
                process = Process(target=self.__worker_function, args=args[i])
                process.start()
                workers.append(process)
            for i, worker in enumerate(workers):
                try:
                    worker.join(timeout=self.__iteration_timeout)
                    if worker.is_alive():
                        worker.terminate()
                        raise Exception("Process timed out")
                    print(f"Result obtained for iteration {i + 1}")
                    task_res, _ = args[i][-1].get()
                    if isinstance(task_res, Exception):
                        data[i].append({"passed": 0, "error": str(task_res)})
                    else:
                        data[i].append(task_res)
                except Exception as e:
                    print(f"Exception for iteration {i + 1}")
                    data[i].append({"passed": 0, "error": str(e)})
            self.__create_and_save_json(data, n_prob, prob_name)
            print(f"\nProblem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        dir_name: str = get_results_dir_path()
        print(f"Results saved in {dir_name}")
        print(f"{'=' * 80}")
        return dir_name

    def run_with_reask(self) -> str:
        print(f"\n{'=' * 80}")
        print(f"Model '{self.__model.name}'")
        for n_prob in range(22, 23):
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            to_save: List[List[Any]] = []
            for iteration in range(self.__iterations):
                print(f"Iteration {iteration + 1}")
                data_not_passed: List[Any] = []
                for rep in range(5):
                    print(f"Repetition {rep + 1}")
                    prompt: str = ""
                    if data_not_passed == []:
                        prompt = self.__problems["Description"][n_prob]
                    else:
                        if data_not_passed != []:
                            temp_prompt: List[str] = ["Below are pairs of values specified as input -> output for which given those input values, "
                                                      "the result obtained from the function you generated is different from the specified "
                                                      "output. If there are multiple input or output values, they are separated by commas. "
                                                      "Correct the previous function according to these specified values in order to pass also this test cases.\n"]
                            for i in range(len(data_not_passed[:20])):
                                temp_prompt.append(str(data_not_passed[i][0]).replace('[', '').replace(']', '') + " -> "
                                                   + str(data_not_passed[i][1]).replace('[', '').replace(']', '') + '\n')
                            prompt = ''.join(temp_prompt)
                    res: Dict[str, List[str]] = self.__ask_model_and_process(prompt)
                    prob_name: str = self.__problems\
                        .get("Problem Name")[n_prob]\
                        .replace(' ', '-')\
                        .lower()
                    args: List[Tuple] = self.__create_task_input(prob_name, res["code"], res["f_names"])
                    data: List[List[Any]] = []
                    for i, arg in enumerate(args):
                        temp = list(arg)
                        temp.pop()
                        temp.append(res["responses"][i])
                        temp.append(res["imports"][i])
                        temp.append(f'{iteration}.{rep}')
                        data.append(temp)
                    workers = []
                    print("Testing...")
                    for i in range(len(args)):
                        process = Process(target=self.__worker_function, args=args[i])
                        process.start()
                        workers.append(process)
                    for i, worker in enumerate(workers):
                        try:
                            worker.join(timeout=self.__iteration_timeout)
                            if worker.is_alive():
                                worker.terminate()
                                raise Exception("Process timed out")
                            print(f"Result obtained for iteration {i + 1}.{rep + 1}")
                            task_res, data_not_passed = args[i][-1].get()
                            if isinstance(task_res, Exception):
                                data[i].append({"passed": 0, "error": str(task_res)})
                            else:
                                data[i].append(task_res)
                        except Exception as e:
                            print(f"Exception for iteration {i + 1}.{rep + 1}")
                            data[i].append({"passed": 0, "error": str(e)})
                    to_save.extend(data)
                print('\n')
            self.__create_and_save_json(to_save, n_prob, prob_name)
            print(f"\nProblem '{prob_name}' completed.")
            print(f"{'=' * 80}")
        dir_name: str = get_results_dir_path()
        print(f"Results saved in {dir_name}")
        print(f"{'=' * 80}")
        return dir_name

    def __ask_model_and_process(self, prompt: str) -> Dict[str, Any]:
        iterations: int = 1 if self.__reask else self.__iterations
        responses: List[str] = []
        code: List[str] = []
        f_imports: List[List[str]] = []
        f_names: List[str] = []
        for iteration in range(iterations):
            if not self.__reask:
                print(f"Iteration {iteration + 1}")
            responses.append(self.__model.ask(prompt))
            try:
                code.append(extract_function(responses[-1]))
            except:
                code.append("")
            try:
                f_imports.append(list(set(extract_external_imports(responses[-1]) +
                                          extract_internal_imports(code[-1]))))
            except:
                f_imports.append([])
            try:
                f_names.append(extract_function_name(code[-1]))
            except:
                f_names.append("")
            if f_imports[-1] != []:
                for imp in f_imports[-1]:
                    if imp not in code[-1]:
                        code[-1] = insert_strings_after_signature(code[-1], [imp])
        return {"responses": responses,
                "code": code,
                "imports": f_imports,
                "f_names": f_names}

    def __create_task_input(self, prob_name: str, f_bodies: List[str], f_names: List[str]) -> List[Tuple]:
        return [(b, n, prob_name, Queue()) for b, n in zip(f_bodies, f_names)]

    def __worker_function(self, *args_with_queue):
        result_queue = args_with_queue[-1]
        try:
            result_queue.put(self.__test_function(*args_with_queue[:-1]))
        except Exception as e:
            result_queue.put(e)

    def __test_function(self, f_body: str, f_name: str, prob_name: str) -> Dict[str, int]:
        try:
            exec(f_body, locals())
        except Exception as e:
            raise Exception("Cannot define function") from e
        else:
            f: Callable = eval(f_name)
            data: Any = self.__dataset_loader.load(prob_name)
            passed: int = 0
            not_passed: int = 0
            with_exception: int = 0
            data_not_passed: List[Any] = []
            for i in range(len(data)):
                args: List[Any] = [v for k, v in data[i].items() if "input" in k]
                expected: List[Any] = [v for k, v in data[i].items() if "output" in k]
                try:
                    result: Any = [f(*args)]
                    if result == expected:
                        passed += 1
                    else:
                        not_passed += 1
                        data_not_passed.append((args, expected))
                except Exception as e:
                    with_exception += 1
                    data_not_passed.append((args, expected))
            return {"passed": passed, "not_passed": not_passed, "with_exception(s)": with_exception}, data_not_passed

    def __create_and_save_json(self, data: List[List[Any]], n_prob: int, prob_name: str) -> None:
        json_data: List[Dict[str, Any]] = []
        json_element: Dict[str, any] = {}
        for element in data:
            formatted_code: str = remove_imports_and_comments_and_format_tabs(element[0])
            imports: List[str] = list(set(e.strip() for e in element[4]))
            code_with_imports: str = insert_strings_after_signature(formatted_code, imports)
            code_no_imports_predefined, used_names = replace_variables_with_names(code_with_imports, imports)
            code_no_imports_predefined: str = remove_imports_and_comments_and_format_tabs(code_no_imports_predefined)
            pony_individual: str = substitute_tabs_and_newlines_with_pony_encode(formatted_code)
            temp: str = ""
            for i in imports:
                temp += i + '#'
            ind: str = temp + substitute_tabs_and_newlines_with_pony_encode(code_no_imports_predefined)
            it: int = 0
            rep: int = 0
            if "." in str(element[5]):
                it = int(element[5].split('.')[0]) + 1
                rep = int(element[5].split('.')[1]) + 1
            else:
                it = element[5] + 1
                rep = 1
            json_element = {
                "iteration": it,
                "repetition": rep,
                "model_response": element[3],
                "imports": imports,
                "variables_names": used_names,
                "function_name": element[1],
                "code": tabs_as_symbol(element[0]),
                "code_no_imports_and_comments": formatted_code,
                "code_imports_and_no_comments": code_with_imports,
                "individual_no_imports": pony_individual,
                "final_individual": ind.replace(element[1], "evolve"),
                "tests_results": element[-1]
            }
            json_data.append(json_element)
        create_and_save_json(
            f"{self.__model.name}{'_problem'}{n_prob}",
            {
                "model_name": self.__model.name,
                "problem_name": prob_name,
                "prompt": self.__problems["Description"][n_prob],
                "problem_index": n_prob,
                "data_test_size": self.__dataset_loader.data_size,
                "data": json_data
            }
        )
