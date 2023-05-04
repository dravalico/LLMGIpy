import pandas
from pandas import DataFrame
from models.AbstractLanguageModel import AbstractLanguageModel
from scripts.json_data_saver import create_json_file
from scripts.individual_formatter import to_pony_individual
import psb2


class ModelTester():
    __VALID_DATASETS: list[str] = ["psb2"]

    def __init__(
            self,
            model: AbstractLanguageModel,
            dataset_name: str,
            data_size: int = 1000,
            iterations: int = 2
    ):
        if not isinstance(model, AbstractLanguageModel):
            e: str = "You must provide an AbstractLanguageModel instance."
            raise Exception(e)
        if not dataset_name in self.__VALID_DATASETS:
            e: str = "You must provide a valid dataset name."
            raise Exception(e)
        self.__model = model
        if dataset_name == "psb2":
            self.__problems: DataFrame = pandas.read_csv(
                "../resources/pbs2_problems_description.csv", sep=";")
        self.__dataset_name = dataset_name
        self.__data_size = data_size
        self.__iterations = iterations

    def run(self) -> None:
        for n_prob in range(0, len(self.__problems)):
            print(f"{'=' * 35}Problem {(n_prob + 1):02d}{'=' * 35}")
            data: list[dict[str, any]] = list()
            for iteration in range(0, self.__iterations):
                print(
                    f"\nIteration {(iteration + 1):02d}\nAsking model '{self.__model.name}'...")
                model_response: any = self.__model.ask(
                    str(self.__problems.get("Description")[n_prob]))
                print("\n{0}\n".format(model_response))
                f_extracted: str = self.__extract_function_body(
                    model_response)
                f_name: str = self.__extract_function_name(
                    f_extracted)
                output: dict[str, any] = {
                    "iteration": (iteration + 1),
                    "model_response": self.__indentation_as_tab(model_response),
                    "function_name": f_name,
                    "function_extracted": self.__indentation_as_tab(f_extracted),
                    "individual": to_pony_individual(self.__indentation_as_tab(f_extracted))
                }
                prob_name: str = self.__problems.get("Problem Name")[n_prob]
                prob_name = prob_name.replace(" ", "-").lower()
                res: dict[str, int] = None
                try:
                    exec(f_extracted, globals())
                    exec("f_to_test = " + f_name, globals())
                    print("Testing...")
                    try:
                        res = self.__test_function(f_to_test, prob_name)
                        output["test_results"] = res
                        print("{:.2f}% passed".format(
                            res["passed"] / self.__data_size * 100))
                        print("Test(s) passed:", res["passed"])
                        print("Test(s) not passed:", res["not_passed"])
                        print("Test(s) with exception(s): " +
                              str(res["with_exception(s)"]) + '\n')
                    except Exception as e:
                        print("Error during tests:", e)
                        output["error"] = str(e)
                except Exception as e:
                    print("Error during definition:", e)
                    output["error"] = str(e)
                data.append(output)
            create_json_file(
                self.__model.name,
                prob_name,
                n_prob + 1,
                data
            )
        print(f"{'=' * 80}\n")

    def __test_function(self, f: callable, prob_name: str) -> dict[str, int]:
        if self.__dataset_name == "psb2":
            test_data = self.__load_psb2_test_data(prob_name)
        passed: int = 0
        not_passed: int = 0
        with_exception: int = 0
        for i in range(0, self.__data_size):
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
            "with_exception(s)": with_exception,
        }

    def __load_psb2_test_data(self, prob_name: str) -> list[tuple[list, list]]:
        try:
            (_, test_data) = psb2.fetch_examples(
                "", prob_name, 0, self.__data_size)
            return test_data
        except:
            raise Exception("Cannot load data for test")

    @staticmethod
    def __extract_function_body(model_response: str) -> str:
        return model_response[model_response.index("def"): len(model_response):]

    @staticmethod
    def __extract_function_name(f: str) -> str:
        return f[f.index("def ") + len("def "): f.index("(")]

    @staticmethod
    def __indentation_as_tab(f: str) -> str:
        f = f.replace("    ", '\t')
        return f.replace("  ", '\t')
