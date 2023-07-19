import pandas
import psb2
from pandas import DataFrame
from typing import List, Tuple


class DatasetLoader():  # TODO Is a good abstraction?
    def __init__(self, dataset: str, data_size: int = 150) -> None:
        self.__data_size: int = data_size
        self.__problems: DataFrame = None
        self.__dataset = dataset
        if dataset == "psb2":
            self.__set_problems_to_psb2()

    def load(self, prob_name: str) -> List[Tuple[List, List]]:
        if self.__dataset == "psb2":
            try:
                (_, test_data) = psb2.fetch_examples("", prob_name, 0, self.__data_size)
                return test_data
            except:
                raise Exception("Cannot load data for test")

    def __set_problems_to_psb2(self) -> None:
        self.__problems = pandas.read_csv("../resources/pbs2_problems_description.csv", sep=";")

    @property
    def problems(self) -> DataFrame:
        return self.__problems

    @property
    def data_size(self) -> int:
        return self.__data_size
