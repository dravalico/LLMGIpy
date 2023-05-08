import pandas
import psb2
from pandas import DataFrame
from typing import List, Tuple


class DatasetLoader():
    def __init__(self, data_size: int = 1000,) -> None:
        self.__data_size: int = data_size
        self.__problems: DataFrame = None

    def set_problems_to_psb2(self) -> None:
        self.__problems: DataFrame = pandas.read_csv(
            "../resources/pbs2_problems_description.csv", sep=";")
    
    @property
    def problems(self) -> DataFrame:
        return self.__problems

    def load_psb2_data(self, prob_name: str) -> List[Tuple[List, List]]:
        try:
            (_, test_data) = psb2.fetch_examples(
                "", prob_name, 0, self.__data_size)
            return test_data
        except:
            raise Exception("Cannot load data for test")
