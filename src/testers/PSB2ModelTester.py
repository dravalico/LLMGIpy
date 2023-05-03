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

    def __init__(
            self,
            model: AbstractLanguageModel,
            iterations: int = 2,
            data_dimension: int = 2000,
    ):
        super().__init__(model)
        self.__iterations = iterations
        self.__data_dimension = data_dimension
        self.__model = model

    def run(self) -> None:
        for n_prob in range(0, len(self.__PROBLEMS)):
            print(f"{'=' * 35}Problem {(n_prob + 1):02d}{'=' * 35}")
            data: list[dict[str, any]] = list()
            for iteration in range(0, self.__iterations):
                print(
                    f"\nIteration {(iteration + 1):02d}\nAsking model '{self.__model.name}'...")
                model_response: any = self.__model.ask(
                    str(self.__PROBLEMS.get("Description")[n_prob]))
                print("\n{0}\n".format(model_response))
                f_extracted: str = super()._extract_function_body(model_response)
                f_name: str = super()._extract_function_name(f_extracted)
                output: dict[str, any] = {
                    "iteration": (iteration + 1),
                    "model_response": super()._indentation_as_tab(model_response),
                    "function_name": f_name,
                    "function_extracted": super()._indentation_as_tab(f_extracted),
                    "individual": to_pony_individual(super()._indentation_as_tab(f_extracted))
                }
                prob_name: str = self.__PROBLEMS.get("Problem Name")[n_prob]
                prob_name = prob_name.replace(" ", "-").lower()
                res: dict[str, int] = None
                try:
                    exec(f_extracted, globals())
                except Exception as e:
                    print("Error during definition:", e)
                else:
                    exec("f_to_test = " + f_name, globals())
                    print("Testing...")
                    try:
                        res = self.__test_function(f_to_test, prob_name)
                    except Exception as e:
                        print("Error during tests:", e)
                        output["error"] = str(e)
                    else:
                        output["results"] = res
                        print("{:.2f}% passed".format(
                            res["passed"] / self.__data_dimension * 100))
                        print("Test(s) passed:", res["passed"])
                        print("Test(s) not passed:", res["not_passed"])
                        print("Test(s) with exception(s): " +
                              str(res["with_exception"]) + '\n')
                data.append(output)
            create_json_file(
                self.__model.name,
                prob_name,
                n_prob + 1,
                data
            )
        print(f"{'=' * 80}\n")

    def __test_function(self, f: Callable, prob_name: str) -> dict[str, int]:
        try:
            (_, test_data) = psb2.fetch_examples(
                "", prob_name, 0, self.__data_dimension)
        except:
            raise Exception("Cannot load data for test")
        else:
            passed: int = 0
            not_passed: int = 0
            with_exception: int = 0
            for i in range(0, len(test_data)):
                args: list[str] = [
                    v for k, v in test_data[i].items() if "input" in k]
                expected_output: list[str] = [
                    v for k, v in test_data[i].items() if "output" in k]
                try:
                    result: any = [f(*args)]
                    if result == expected_output:
                        passed = passed + 1
                    else:
                        not_passed = not_passed + 1
                except:
                    with_exception = with_exception + 1
            return {
                "passed": passed,
                "not_passed": not_passed,
                "with_exception": with_exception,
            }
