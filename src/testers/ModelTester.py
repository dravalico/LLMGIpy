from typing import List, Any, Dict, Callable
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from multiprocessing import cpu_count
from pandas import DataFrame
from testers.DatasetLoader import DatasetLoader
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_and_save_json, get_results_dir_path
from scripts.function_util import (extract_imports,
                                   extract_function,
                                   extract_function_name,
                                   tabs_as_symbol,
                                   remove_imports_and_comments_and_format_tabs)
from scripts.ponyge.individual_formatter import to_pony_individual


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
        print(f"Asking model '{self.__model.name}'...")
        for n_prob in range(len(self.__problems)):
            print(f"{'=' * 35}Problem {(n_prob):02d}{'=' * 35}")
            res: Dict[str, List[str]] = self.__ask_model_and_process(n_prob)
            prob_name: str = self.__problems\
                .get("Problem Name")[n_prob]\
                .replace(' ', '-')\
                .lower()  # NOTE Maybe it's better if all the problem files have a directly correct name
            n_threads: int = cpu_count() if self.__iterations > cpu_count() else self.__iterations
            with ThreadPoolExecutor(max_workers=n_threads) as executor:
                futures_dict: Dict[Future, List[Any]] = self.__create_futures(
                    executor,
                    prob_name,
                    res["code"],
                    res["f_names"]
                )
                for i, (_, item) in enumerate(futures_dict.items()):
                    item.append(res["responses"][i])
                    item.append(res["imports"][i])
                futures: List[Future] = list(futures_dict.keys())
                json_data: List[Dict[str, Any]] = []
                json_element: Dict[str, any] = {}
                print("\nTesting...")
                for future in futures:
                    formatted_code: str = remove_imports_and_comments_and_format_tabs(futures_dict[future][2])
                    imports: List[str] = futures_dict[future][5]
                    json_element = {  # NOTE is this elegant?
                        "iteration": futures_dict[future][1] + 1,
                        "model_response": futures_dict[future][4],
                        "imports": imports,
                        "function_name": futures_dict[future][3],
                        "code": tabs_as_symbol(futures_dict[future][2]),
                        "code_without_imports_and_comments": formatted_code,
                        "individual": to_pony_individual(formatted_code, imports)
                    }
                    try:
                        result: Any = future.result(timeout=self.__iteration_timeout)
                        print("Result obtained for iteration", futures_dict[future][1] + 1)
                    except Exception as e:
                        print("Exception for iteration", futures_dict[future][1] + 1)
                        if isinstance(e, TimeoutError):
                            e = "Timeout for tests"
                            future.cancel()
                        result = {"error": str(e)}
                    json_element["tests_results"] = result
                    json_data.append(json_element)
                print("\nSaving results...")
            create_and_save_json(
                f"{self.__model.name}{'_problem'}{n_prob}",
                {
                    "model_name": self.__model.name,
                    "problem_name": prob_name,
                    "problem_index": n_prob,
                    "data": json_data
                }
            )
            print(f"Problem '{prob_name}' completed.")
        print(f"{'=' * 80}")
        dir_name: str = get_results_dir_path()
        print(f"Results saved in {dir_name}")
        print(f"{'=' * 80}")
        return dir_name

    def __ask_model_and_process(self, n_prob: int) -> Dict[str, List[str]]:
        responses: List[str] = []
        code: List[str] = []
        f_imports: List[str] = []
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
                f_imports.append(extract_imports(responses[-1]))
            except:
                f_imports.append([])
            try:
                f_names.append(extract_function_name(code[-1]))
            except:
                f_names.append("")
        return {"responses": responses,
                "code": code,
                "imports": f_imports,
                "f_names": f_names}

    def __create_futures(self, executor: ThreadPoolExecutor, prob_name: str, f_bodies: List[str], f_names: List[str]) -> Dict[Future, List[Any]]:
        futures: List[Future] = [executor.submit(self.__test_function, b, n, prob_name)
                                 for b, n in zip(f_bodies, f_names)]
        return {f: [prob_name, i, f_bodies[i], f_names[i]] for i, f in enumerate(futures)}

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
