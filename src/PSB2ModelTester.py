from typing import Callable
import pandas
import psb2
import AbstractLanguageModel
import AbstractModelTester


class PSB2ModelTester(AbstractModelTester.AbstractModelTester):
    __PROBLEMS_CSV = pandas.DataFrame = pandas.read_csv(
        "/mnt/data/dravalico/ImprovementLLM/resources/pbs2_problems_description.csv",
        sep=";",
    )
    __test_iteration: int = 0
    __test_data_dimension: int = 0
    __model_to_test: AbstractLanguageModel.AbstractLanguageModel = None

    def __init__(
        self,
        test_iteration: int,
        test_data_dimension: int,
        model: AbstractLanguageModel.AbstractLanguageModel,
    ):
        super().__init__()
        self.__test_iteration = test_iteration
        self.__test_data_dimension = test_data_dimension
        self.__model_to_test = model

    def run(self) -> None:
        super().run()
        for i in range(0, len(self.__PROBLEMS_CSV)):
            mean_test_results = [0, 0, 0]
            print("===============================")
            print("Problem n." + str(i + 1))
            for j in range(0, self.__test_iteration):
                print("\nIteration n." + str(j + 1) + "\nAsking model...")
                model_response = self.__model_to_test.ask(
                    str(self.__PROBLEMS_CSV.get("Description")[i])
                )
                print()
                print(model_response)
                print()
                print("Answer obtained\nExtracting function...")
                function_body = self.__extract_function_body(model_response)
                try:
                    exec(function_body)
                    print("Function extracted and ready")
                    function_name = self.__extract_function_name(function_body)
                    function_extracted: object = any
                    exec("function_extracted = " + function_name)
                    problem_name = self.__PROBLEMS_CSV.get("Problem Name")[i].lower()
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
                except:
                    print("Error during definition or testing of the function")
            print()
            print(
                "Avg passed: " + str(int(mean_test_results[0] / self.__test_iteration))
            )
            print(
                "Avg not passed: "
                + str(int(mean_test_results[1] / self.__test_iteration))
            )
            print(
                "Avg exception: "
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
        print("===============================")
        print()

    def __extract_function_body(self, model_response: str) -> str:
        return model_response[model_response.index("def") : len(model_response) :]

    def __extract_function_name(self, function_body: str) -> str:
        # function_name = regex.findall("\s*(def)\s(.*?)\([a-zA-z]*\)", extracted_function)
        return function_body[
            function_body.index("def ") + len("def ") : function_body.index("(")
        ]

    def __test_function(
        self, function_to_test: Callable, problem_name: str
    ) -> dict[str, int]:
        (train_data, test_data) = psb2.fetch_examples(
            "", problem_name, 0, self.test_data_dimension
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
                result = [function_to_test(*args)]
                if str(result) == str(expected_output):
                    test_passed = test_passed + 1
                else:
                    test_not_passed = test_not_passed + 1
            except Exception as e:
                test_with_exception = test_with_exception + 1
        return {
            "test_passed": test_passed,
            "test_not_passed": test_not_passed,
            "test_with_exception": test_with_exception,
        }
