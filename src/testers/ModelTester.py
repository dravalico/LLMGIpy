from typing import List, Any, Dict, Callable
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_and_save_json
from scripts.function_util import to_pony_individual, extract_function_from_str, extract_function_name, tabs_as_symbol
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from multiprocessing import cpu_count
from pandas import DataFrame


class ModelTester():
    def __init__(  # TODO Check if args are ok
            self,
            model: AbstractLanguageModel,
            problems: DataFrame,
            dataset_loader: Callable,
            iterations: int = 5,
            iteration_timeout: int = 60
    ) -> None:
        if not isinstance(model, AbstractLanguageModel):
            e: str = "You must provide an AbstractLanguageModel instance."
            raise Exception(e)
        self.__model: AbstractLanguageModel = model
        self.__problems: DataFrame = problems
        self.__dataset_loader: Callable = dataset_loader
        self.__iterations: int = iterations
        self.__iteration_timeout: int = iteration_timeout

    def run(self) -> None:
        print(f"{'=' * 80}")
        print(f"Asking model '{self.__model.name}'...")
        for n_prob in range(len(self.__problems)):
            print(f"{'=' * 35}Problem {(n_prob + 1):02d}{'=' * 35}")
            res: Dict[str, List[str]] = self.__ask_model_and_process(n_prob)
            prob_name: str = self.__problems\
                .get("Problem Name")[n_prob]\
                .replace(" ", "-")\
                .lower()  # TODO Maybe it's better if all the problem files have a directly correct name
            n_threads: int = cpu_count() if self.__iterations > cpu_count() else self.__iterations
            with ThreadPoolExecutor(max_workers=n_threads) as executor:
                futures_dict: Dict[Future, List[Any]] = self.__create_futures(
                    executor,
                    prob_name,
                    res["f_bodies"],
                    res["f_names"]
                )
                for i, (_, item) in enumerate(futures_dict.items()):
                    item.append(res["responses"][i])
                futures: List[Future] = list(futures_dict.keys())
                json_data: List[Dict[str, Any]] = []
                json_element: Dict[str, any] = {}
                print("\nTesting...")
                for future in futures:
                    json_element = {
                        "iteration": (futures_dict[future][1] + 1),
                        "model_response": futures_dict[future][4],
                        "function_name": futures_dict[future][3],
                        "function_extracted": tabs_as_symbol(futures_dict[future][2]),
                        "individual": to_pony_individual(tabs_as_symbol(futures_dict[future][2]))
                    }
                    try:
                        result: Any = future.result(timeout=self.__iteration_timeout)
                        print("Result obtained for iteration", futures_dict[future][1])
                    except Exception as e:
                        print("Exception for iteration", futures_dict[future][1])
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
        print(f"{'=' * 80}\n")

    def __ask_model_and_process(self, n_prob: int) -> Dict[str, List[str]]:
        responses: List[str] = []
        f_bodies: List[str] = []
        f_names: List[str] = []
        for iteration in range(self.__iterations):
            print(f"Iteration {iteration}")
            description: str = self.__problems["Description"][n_prob]
            responses.append(self.__model.ask(description))
            f_bodies.append(extract_function_from_str(responses[-1]))
            f_names.append(extract_function_name(f_bodies[-1]))
        return {"responses": responses, "f_bodies": f_bodies, "f_names": f_names}

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
            data: Any = self.__dataset_loader(prob_name)
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