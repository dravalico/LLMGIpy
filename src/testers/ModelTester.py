from typing import List, Tuple, Any, Dict
import pandas
import psb2
from pandas import DataFrame
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_and_save_json
from scripts.individual_formatter import to_pony_individual
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from multiprocessing import cpu_count


class ModelTester():
    __VALID_DATASETS: List[str] = ["psb2"]

    def __init__(
            self,
            model: AbstractLanguageModel,
            dataset_name: str,
            data_size: int = 1000,
            iterations: int = 2,
            iteration_timeout: int = 30
    ) -> None:
        if not isinstance(model, AbstractLanguageModel):
            e: str = "You must provide an AbstractLanguageModel instance."
            raise Exception(e)
        if not dataset_name in self.__VALID_DATASETS:
            e: str = "You must provide a valid dataset name."
            raise Exception(e)
        self.__model: AbstractLanguageModel = model
        if dataset_name == "psb2":
            self.__problems: DataFrame = pandas.read_csv(
                "../resources/pbs2_problems_description.csv", sep=";")
        self.__dataset_name: str = dataset_name
        self.__data_size: int = data_size
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
                .lower()
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
                json_element: dict[str, any] = {}
                print("\nTesting...")
                for future in futures:
                    json_element = {
                        "iteration": futures_dict[future][1],
                        "model_response": futures_dict[future][4],
                        "function_name": futures_dict[future][3],
                        "function_extracted": self.__format_tab(futures_dict[future][2]),
                        "individual": to_pony_individual(self.__format_tab(futures_dict[future][2]))
                    }
                    try:
                        result: Any = future.result(
                            timeout=self.__iteration_timeout)
                        print("Result obtained for iteration",
                              futures_dict[future][1])
                    except Exception as e:
                        print("Exception for iteration",
                              futures_dict[future][1])
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
                    "problem_number": n_prob,
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
            f_bodies.append(self.__extract_function(responses[-1]))
            f_names.append(self.__extract_function_name(f_bodies[-1]))
        return {"responses": responses, "f_bodies": f_bodies, "f_names": f_names}

    def __create_futures(self, executor: ThreadPoolExecutor, prob_name: str, f_bodies: List[str], f_names: List[str]) -> Dict[Future, List[Any]]:
        futures: List[Future] = [
            executor.submit(self.__test_function, b, n, prob_name)
            for b, n in zip(f_bodies, f_names)]
        return {f: [prob_name, i, f_bodies[i], f_names[i]] for i, f in enumerate(futures)}

    def __test_function(self, f_body: str, f_name: str, prob_name: str) -> Dict[str, int]:
        try:
            exec(f_body, locals())
        except Exception as e:
            raise Exception("Cannot define function") from e
        else:
            f: callable = eval(f_name)
            if self.__dataset_name == "psb2":
                data = self.__load_psb2_data(prob_name)
            passed: int = 0
            not_passed: int = 0
            with_exception: int = 0
            for i in range(self.__data_size):
                args: List[str] = [
                    v for k, v in data[i].items() if "input" in k]
                expected: List[str] = [
                    v for k, v in data[i].items() if "output" in k]
                try:
                    result: Any = [f(*args)]
                    if result == expected:
                        passed += 1
                    else:
                        not_passed += 1
                except Exception as e:
                    with_exception += 1
            return {"passed": passed, "not_passed": not_passed, "with_exception(s)": with_exception}

    def __load_psb2_data(self, prob_name: str) -> List[Tuple[List, List]]:
        try:
            (_, test_data) = psb2.fetch_examples(
                "", prob_name, 0, self.__data_size)
            return test_data
        except:
            raise Exception("Cannot load data for test")

    @staticmethod
    def __extract_function(output: str) -> str:
        return output[output.index("def"): len(output):]

    @staticmethod
    def __extract_function_name(f: str) -> str:
        return f[f.index("def ") + len("def "): f.index("(")]

    @staticmethod
    def __format_tab(f: str) -> str:
        return f.replace("    ", '\t').replace("  ", '\t')
