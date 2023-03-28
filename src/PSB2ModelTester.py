from typing import Callable
import pandas
from pandas import DataFrame
import psb2
from AbstractLanguageModel import AbstractLanguageModel
from AbstractModelTester import AbstractModelTester


class PSB2ModelTester(AbstractModelTester):
    __PROBLEMS_CSV: DataFrame = pandas.read_csv(
        "/mnt/data/dravalico/LLMGIpy/resources/pbs2_problems_description.csv",
        sep=";",
    )
    __test_iteration: int = 0
    __test_data_dimension: int = 0
    __model_to_test: AbstractLanguageModel = None

    def __init__(
        self,
        test_iteration: int,
        test_data_dimension: int,
        model: AbstractLanguageModel,
    ):
        super().__init__()
        self.__test_iteration = test_iteration
        self.__test_data_dimension = test_data_dimension
        self.__model_to_test = model

    def run(self) -> None:
        super().run()
        for i in range(0, len(self.__PROBLEMS_CSV)):
            mean_test_results: list[int, int, int] = [0, 0, 0]
            print(f"===============Problem {(i + 1):02d}===============")
            for j in range(0, self.__test_iteration):
                print(
                    "Iteration {0}\nAsking model '{1}'...".format(
                        str(j + 1), self.__model_to_test.get_model_name()
                    )
                )
                model_response: any = self.__model_to_test.ask(
                    str(self.__PROBLEMS_CSV.get("Description")[i])
                )
                print()
                print(model_response)
                print()
                function_body: str = super()._extract_function_body(model_response)
                try:
                    exec(function_body, globals())
                    function_name: str = super()._extract_function_name(function_body)
                    exec("function_extracted = " + function_name, globals())
                    problem_name: str = self.__PROBLEMS_CSV.get("Problem Name")[
                        i
                    ].lower()
                    problem_name = problem_name.replace(" ", "-")
                    print("Starting tests...")
                    results: dict[str, int] = self.__test_function(
                        function_extracted, problem_name
                    )
                    mean_test_results[0] = mean_test_results[0] + results["test_passed"]
                    mean_test_results[1] = (
                        mean_test_results[1] + results["test_not_passed"]
                    )
                    mean_test_results[2] = (
                        mean_test_results[2] + results["test_with_exception"]
                    )
                except Exception as e:
                    print("Error during definition: " + e)
            print()
            print(
                "Avg test passed: "
                + str(int(mean_test_results[0] / self.__test_iteration))
            )
            print(
                "Avg test not passed: "
                + str(int(mean_test_results[1] / self.__test_iteration))
            )
            print(
                "Avg test with exception: "
                + str(int(mean_test_results[2] / self.__test_iteration))
            )
            print(
                str(
                    (mean_test_results[0] / self.__test_iteration)
                    / self.__test_data_dimension
                    * 100
                )
                + "%"
            )
            print("========================================")
            print()

    def __test_function(
        self, function_to_test: Callable, problem_name: str
    ) -> dict[str, int]:
        (train_data, test_data) = psb2.fetch_examples(
            "", problem_name, 0, self.__test_data_dimension
        )
        test_passed: int = 0
        test_not_passed: int = 0
        test_with_exception: int = 0
        for i in range(0, len(test_data)):
            args: list[str] = [v for k, v in test_data[i].items() if "input" in k]
            expected_output: list[str] = [
                v for k, v in test_data[i].items() if "output" in k
            ]
            try:
                result: any = [function_to_test(*args)]
                if str(result) == str(expected_output):
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
