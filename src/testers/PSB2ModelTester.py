from typing import Callable
import pandas
from pandas import DataFrame
import psb2
from testers.AbstractModelTester import AbstractModelTester
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.JSON_data_saver import create_json_file
from scripts.individual_formatter import to_pony_individual


class PSB2ModelTester(AbstractModelTester):
    __PROBLEMS: DataFrame = pandas.read_csv(
        "../resources/pbs2_problems_description.csv", sep=";")
    __test_iteration: int = 0
    __test_data_dimension: int = 0
    __model_to_test: AbstractLanguageModel = None

    def __init__(
            self,
            model: AbstractLanguageModel,
            test_iterations: int = 1,
            test_data_dimension: int = 2000,
    ):
        super().__init__()
        self.__test_iteration = test_iterations
        self.__test_data_dimension = test_data_dimension
        self.__model_to_test = model

    def run(self) -> None:
        for n_prob in range(0, len(self.__PROBLEMS)):
            print(f"{'=' * 35}Problem {(n_prob + 1):02d}{'=' * 35}")
            data: list[dict[str, any]] = list()
            for iteration in range(0, self.__test_iteration):
                print(
                    f"\nIteration {(iteration + 1):02d}\nAsking model '{self.__model_to_test.name}'...")
                model_response: any = self.__model_to_test.ask(
                    str(self.__PROBLEMS.get("Description")[n_prob]))
                print("\n{0}\n".format(model_response))
                function_extracted: str = super()._extract_function_body(model_response)
                function_name: str = super()._extract_function_name(function_extracted)
                output: dict[str, any] = {
                    "iteration": (iteration + 1),
                    "model_response": model_response.replace("    ", "\t"),
                    "function_name": function_name,
                    "individual": to_pony_individual(function_extracted.replace("    ", "\t"))
                }
                problem_name: str = self.__PROBLEMS.get("Problem Name")[n_prob]
                problem_name = problem_name.replace(" ", "-").lower()
                tests_results: dict[str, int] = None
                try:
                    exec(function_extracted, globals())
                except Exception as e:
                    print("Error during definition:", e)
                else:
                    exec("function_to_test = " + function_name, globals())
                    print("Testing...")
                    try:
                        tests_results = self.__test_function(
                            function_to_test, problem_name)
                    except Exception as e:
                        print("Error during tests:", e)
                        output["error"] = str(e)
                    else:
                        output["results"] = tests_results
                        print("{:.2f}% passed".format(
                            tests_results["test_passed"] / self.__test_data_dimension * 100))
                        print("Test(s) passed:", tests_results["test_passed"])
                        print("Test(s) not passed:",
                              tests_results["test_not_passed"])
                        print("Test(s) with exception(s): " +
                              str(tests_results["test_with_exception"]) + '\n')
                data.append(output)
            create_json_file(
                    self.__model_to_test.name,
                    problem_name,
                    n_prob + 1,
                    data
                )
        print(f"{'=' * 80}\n")

    def __test_function(self, function_to_test: Callable, problem_name: str) -> dict[str, int]:
        try:
            (train_data, test_data) = psb2.fetch_examples(
                "", problem_name, 0, self.__test_data_dimension)
        except:
            raise Exception("Cannot load data for test")
        else:
            test_passed: int = 0
            test_not_passed: int = 0
            test_with_exception: int = 0
            for i in range(0, len(test_data)):
                args: list[str] = [
                    v for k, v in test_data[i].items() if "input" in k]
                expected_output: list[str] = [
                    v for k, v in test_data[i].items() if "output" in k]
                try:
                    result: any = [function_to_test(*args)]
                    if result == expected_output:
                        test_passed = test_passed + 1
                    else:
                        test_not_passed = test_not_passed + 1
                except:
                    test_with_exception = test_with_exception + 1
            return {
                "test_passed": test_passed,
                "test_not_passed": test_not_passed,
                "test_with_exception": test_with_exception,
            }
