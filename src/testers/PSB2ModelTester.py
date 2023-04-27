from typing import Callable
import pandas
from pandas import DataFrame
import psb2
from testers.AbstractModelTester import AbstractModelTester
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.JSON_data_saver import create_json_file


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
            avg_test_output: list[int, int, int] = [0, 0, 0]
            print(f"{'=' * 35}Problem {(n_prob + 1):02d}{'=' * 35}")
            for iteration in range(0, self.__test_iteration):
                print(
                    f"Iteration {(iteration + 1):02d}\nAsking model '{self.__model_to_test.name}'...")
                model_response: any = self.__model_to_test.ask(
                    str(self.__PROBLEMS.get("Description")[n_prob]))
                print("\n{0}\n".format(model_response))
                function_body: str = super()._extract_function_body(model_response)
                function_name: str = super()._extract_function_name(function_body)
                problem_name: str = self.__PROBLEMS.get("Problem Name")[n_prob]
                problem_name = problem_name.replace(" ", "-").lower()
                error_str: str = ""
                test_results: dict[str, int] = None
                try:
                    exec(function_body, globals())
                except Exception as e:
                    print("Error during definition:", e)
                    error_str = str(e)
                else:
                    exec("function_extracted = " + function_name, globals())
                    print("Starting tests...")
                    try:
                        test_results = self.__test_function(
                            function_extracted, problem_name)
                    except Exception as e:
                        print("Error during tests:", e)
                        error_str = str(e)
                    else:
                        avg_test_output[0] = avg_test_output[0] + \
                            test_results["test_passed"]
                        avg_test_output[1] = avg_test_output[1] + \
                            test_results["test_not_passed"]
                        avg_test_output[2] = avg_test_output[2] + \
                            test_results["test_with_exception"]
                        print("{:.2f}% passed".format(
                            (avg_test_output[0] / self.__test_iteration) / self.__test_data_dimension * 100))
                        print(
                            f"{'Avg test passed:'}{int(avg_test_output[0] / self.__test_iteration)}")
                        print(
                            f"{'Avg test not passed:'}{int(avg_test_output[1] / self.__test_iteration)}")
                        print(
                            f"{'Avg test with exception(s):'}{int(avg_test_output[2] / self.__test_iteration)}")
                        print(f"{'=' * 80}\n")
                create_json_file(
                    self.__model_to_test.name,
                    problem_name,
                    n_prob + 1,
                    iteration + 1,
                    model_response,
                    test_results,
                    error_str
                )
                print("Results saved\n")

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
