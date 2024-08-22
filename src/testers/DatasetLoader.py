import pandas as pd
import json
import random
from typing import List, Tuple, Any


class DatasetLoader():
    def __init__(self, dataset: str, train_size: int, test_size: int = 1000) -> None:
        self.__train_size: int = train_size
        self.__test_size: int = test_size
        self.__dataset: str = dataset
        self.__dataset_folder: str = f"../PonyGE2/datasets/progsys/{dataset}-bench/"
        self.__problems: pd.DataFrame = pd.read_json(self.__dataset_folder + 'descr.json', orient='records')
        with open(self.__dataset_folder + 'n_inputs.json', 'r') as json_file:
            n_inputs = json.load(json_file)
        self.__n_inputs: dict[str, int] = {key: int(n_inputs[key]) for key in n_inputs}

    def load(self, prob_name: str, n_iter: int) -> Tuple[Tuple[List[Any], List[Any]], Tuple[List[Any], List[Any]]]:
        with open(self.__dataset_folder + prob_name + '/' + 'Train.txt', 'r') as f:
            c = f.read()
            exec(c, globals())
            train_data = (inval[:], outval[:]) # type: ignore
        
        with open(self.__dataset_folder + prob_name + '/' + 'Test.txt', 'r') as f:
            c = f.read()
            exec(c, globals())
            test_data = (inval[:self.__test_size], outval[:self.__test_size]) # type: ignore
        
        return self.__train_shuffle(train_data, n_iter), test_data

    def __train_shuffle(self, data: Tuple[List[Any], List[Any]], n_iter: int) -> Tuple[List[Any], List[Any]]:
        inval, outval = data
        if len(inval) != len(outval):
            raise ValueError(f'Length mismatch between inval ({len(inval)}) and outval ({len(outval)}).')
        indices: list[int] = list(range(len(inval)))
        random.Random(24 + 31 * n_iter * n_iter).shuffle(indices)
        new_inval = []
        new_outval = []
        for i in indices[:self.__train_size]:
            new_inval.append(inval[i])
            new_outval.append(outval[i])
        return new_inval, new_outval

    def get_n_inputs(self, problem_name: str) -> int:
        return self.__n_inputs[problem_name.strip().replace(' ', '-').lower()]

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
