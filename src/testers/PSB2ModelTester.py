from typing import Callable
import pandas
from pandas import DataFrame
import psb2
from testers.AbstractModelTester import AbstractModelTester
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.JSON_data_saver import create_json_file


class PSB2ModelTester(AbstractModelTester):
    __PROBLEMS_CSV: DataFrame = pandas.read_csv("../resources/pbs2_problems_description.csv", sep=";")
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
        for i in range(0, len(self.__PROBLEMS_CSV)):
            avg_test_output: list[int, int, int] = [0, 0, 0]
            print(f"{'=' * 20}Problem {(i + 1):02d}{'=' * 20}")
            for j in range(0, self.__test_iteration):
                print(f"Iteration {(j + 1):02d}\nAsking model '{self.__model_to_test.name}'...")
                model_response: any = self.__model_to_test.ask(str(self.__PROBLEMS_CSV.get("Description")[i]))
                print("\n{0}\n".format(model_response))
                function_body: str = super()._extract_function_body(model_response)
                function_name: str = super()._extract_function_name(function_body)
                problem_name: str = self.__PROBLEMS_CSV.get("Problem Name")[i].lower()
                problem_name = problem_name.replace(" ", "-")
                error: bool = False
                try:
                    exec(function_body, globals())
                except Exception as e:
                    print("Error during definition:", e)
                    error = True
                else:
                    exec("function_extracted = " + function_name, globals())
                    print("Starting tests...")
                    test_output: dict[str, int] = self.__test_function(function_extracted, problem_name)
                    avg_test_output[0] = avg_test_output[0] + test_output["test_passed"]
                    avg_test_output[1] = avg_test_output[1] + test_output["test_not_passed"]
                    avg_test_output[2] = avg_test_output[2] + test_output["test_with_exception"]
                    print("Results saved\n")
                create_json_file(
                        self.__model_to_test.name,
                        i + 1,
                        j + 1,
                        model_response,
                        test_output if not error else "Error during definition"
                    )
            passed_percentage: float = (avg_test_output[0] / self.__test_iteration) / self.__test_data_dimension * 100
            print("{:.2f}% passed".format(passed_percentage))
            print("Avg test passed:", int(avg_test_output[0] / self.__test_iteration))
            print("Avg test not passed:", int(avg_test_output[1] / self.__test_iteration))
            print("Avg test with exception:", int(avg_test_output[2] / self.__test_iteration))
            print(f"{'=' * 50}\n")

    def __test_function(self, function_to_test: Callable, problem_name: str) -> dict[str, int]:
        (train_data, test_data) = psb2.fetch_examples("", problem_name, 0, self.__test_data_dimension)
        test_passed: int = 0
        test_not_passed: int = 0
        test_with_exception: int = 0
        for i in range(0, len(test_data)):
            args: list[str] = [v for k, v in test_data[i].items() if "input" in k]
            expected_output: list[str] = [v for k, v in test_data[i].items() if "output" in k]
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
