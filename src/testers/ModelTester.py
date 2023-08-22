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
from scripts.ponyge.individual_formatter import (to_pony_individual_with_imports,
                                                 substitute_tabs_and_newlines_with_pony_encode,
                                                 substitute_variables_name,
                                                 extract_variables_names,
                                                 substitute_variables_name_with_predefined)


class ModelTester():
    def __init__(  # TODO Check if args are ok
            self,
            model: AbstractLanguageModel,
            dataset_loader: DatasetLoader,
            iterations: int = 5,
            iteration_timeout: int = 60
    ) -> None:
        if (not isinstance(model, AbstractLanguageModel)) or (model == None):
            e: str = "You must provide an AbstractLanguageModel instance."
            raise Exception(e)
        self.__model: AbstractLanguageModel = model
        self.__dataset_loader: DatasetLoader = dataset_loader
        self.__problems: DataFrame = self.__dataset_loader.problems
        self.__iterations: int = iterations
        self.__iteration_timeout: int = iteration_timeout

    def run(self) -> str:
        print(f"\n{'=' * 80}")
        print(f"Model '{self.__model.name}'")
        for n_prob in range(len(self.__problems)):
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            res: Dict[str, List[str]] = self.__ask_model_and_process(n_prob)
            prob_name: str = self.__problems\
                .get("Problem Name")[n_prob]\
                .replace(' ', '-')\
                .lower()  # NOTE Maybe it's better if all the problem files have a directly correct name
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
                    task_res: Any = args[i][-1].get()
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

    def __ask_model_and_process(self, n_prob: int) -> Dict[str, Any]:
        responses: List[str] = []
        code: List[str] = []
        f_imports: List[List[str]] = []
        f_names: List[str] = []
        for iteration in range(self.__iterations):
            print(f"Iteration {iteration + 1}")
            description: str = self.__problems["Description"][n_prob]
            responses.append(self.__model.ask(description))
            try:  # TODO check if this management is ok
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
            for i in range(len(data)):
                args: List[str] = [v for k, v in data[i].items() if "input" in k]
                expected: List[str] = [v for k, v in data[i].items() if "output" in k]
                try:
                    result: Any = [f(*args)]
                    if result == expected:
                        passed += 1
                    else:
                        not_passed += 1
                except Exception as e:
                    with_exception += 1
            return {"passed": passed, "not_passed": not_passed, "with_exception(s)": with_exception}

    def __create_and_save_json(self, data: List[List[Any]], n_prob: int, prob_name: str) -> None:
        json_data: List[Dict[str, Any]] = []
        json_element: Dict[str, any] = {}
        for element in data:
            formatted_code: str = remove_imports_and_comments_and_format_tabs(element[0])
            imports: List[str] = element[4]
            code_with_imports: str = insert_strings_after_signature(formatted_code, imports)
            code_with_imports_predefined, _ = substitute_variables_name_with_predefined(
                extract_variables_names(code_with_imports), code_with_imports)
            code_no_imports_predefined, used_names = substitute_variables_name_with_predefined(extract_variables_names(code_with_imports), code_with_imports)
            code_no_imports_predefined = remove_imports_and_comments_and_format_tabs(code_no_imports_predefined)
            pony_individual: str = substitute_tabs_and_newlines_with_pony_encode(formatted_code)
            imports_predefined = extract_internal_imports(code_with_imports_predefined)
            temp = ""
            for i in imports_predefined:
                temp += i + '#'
            ind = temp + substitute_tabs_and_newlines_with_pony_encode(code_no_imports_predefined)
            json_element = {
                "iteration": element[5] + 1,
                "model_response": element[3],
                "imports": imports,
                "imports_predefined": imports_predefined,
                "variables_names": used_names,
                "function_name": element[1],
                "code": tabs_as_symbol(element[0]),
                "code_no_imports_and_comments": formatted_code,
                "code_no_imports_and_comments_predefined_vars": code_no_imports_predefined,
                "code_imports_and_no_comments": code_with_imports,
                "code_imports_and_no_comments_predefined_vars": code_with_imports_predefined,
                "individual_no_imports": pony_individual,
                "individual_no_imports_predefined_vars": substitute_tabs_and_newlines_with_pony_encode(code_no_imports_predefined),
                "individual_imports": to_pony_individual_with_imports(formatted_code, imports),
                "individual_imports_predefined_vars": substitute_tabs_and_newlines_with_pony_encode(code_with_imports_predefined),
                "final_individual": ind.replace(element[1], "evolve"),
                "tests_results": element[-1]
            }
            json_data.append(json_element)
        create_and_save_json(
            f"{self.__model.name}{'_problem'}{n_prob}",
            {
                "model_name": self.__model.name,
                "problem_name": prob_name,
                "problem_index": n_prob,
                "data_test_size": self.__dataset_loader.data_size,
                "data": json_data
            }
        )
