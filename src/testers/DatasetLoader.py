import pandas as pd
from typing import List, Tuple, Any


class DatasetLoader():
    def __init__(self, dataset: str, train_size: int, test_size: int = 1000) -> None:
        self.__train_size: int = train_size
        self.__test_size: int = test_size
        self.__dataset: str = dataset
        self.__dataset_folder: str = f"../PonyGE2/datasets/progsys/{dataset}-bench/"
        self.__problems: pd.DataFrame = pd.read_json(self.__dataset_folder + 'descr.json', orient='records')

    def load(self, prob_name: str) -> Tuple[Tuple[List[Any], List[Any]]]:
        with open(self.__dataset_folder + prob_name + '/' + 'Train.txt', 'r') as f:
            c = f.read()
            exec(c, globals())
            train_data = (inval[:self.__train_size], outval[:self.__train_size]) # type: ignore
        
        with open(self.__dataset_folder + prob_name + '/' + 'Test.txt', 'r') as f:
            c = f.read()
            exec(c, globals())
            test_data = (inval[:self.__test_size], outval[:self.__test_size]) # type: ignore
        
        return train_data, test_data
            
    @property
    def dataset(self) -> str:
        return self.__dataset
    
    @property
    def problems(self) -> pd.DataFrame:
        return self.__problems

    @property
    def train_size(self) -> int:
        return self.__train_size
    
    @property
    def test_size(self) -> int:
        return self.__test_size
