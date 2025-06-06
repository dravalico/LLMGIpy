import os
from collections.abc import Callable
from typing import Any, TypeVar, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
import multiprocessing as mp

T = TypeVar('T')


def fake_parallelize(target_method: Callable, parameters: list[dict[str, Any]], num_workers: int = 0, chunksize: int = 1, timeout: Optional[float] = None) -> list[T]:
    return [target_method(**t) for t in parameters]


def thread_pool_parallelize(target_method: Callable, parameters: list[dict[str, Any]], num_workers: int = 0, chunksize: int = 1, timeout: Optional[float] = None) -> list[T]:
    """
    ThreadPoolExecutor with the specification of the number of workers (default 0, meaning no parallelization).
    The parameter num_workers in this case is an int that must be in the range [-2, cpu_count]:
    - -2 means that number of workers is set to be equal to the total number of cores in your machine;
    - -1 means that number of workers is set to be equal to the total number of cores in your machine minus 1 (a single core remains free of work, so that the system is less likely to get frozen during the execution of the method);
    - 0 means that no parallelization is performed;
    - a strictly positive value means that the number of workers is set to be equal to the exact specified number which, of course, must not be higher than the available cores.
    Moreover, the chunksize parameter is provided, which corresponds to the chunksize parameter of the map method.
    """
    if num_workers < -2:
        raise AttributeError(f"Specified an invalid number of cores {num_workers}: this is a negative number lower than -2.")
    if num_workers > os.cpu_count():
        raise AttributeError(f"Specified a number of cores ({num_workers}) that is greater than the number of cores supported by your computer ({os.cpu_count()}).")
    
    if num_workers == 0:
        return [target_method(**t) for t in parameters]

    number_of_processes: int = {-2: (os.cpu_count()), -1: (os.cpu_count() - 1)}.get(num_workers, num_workers)
        
    with ThreadPoolExecutor(max_workers=number_of_processes) as executor:
        map_function: Callable = partial(executor.map, chunksize=chunksize, timeout=timeout)
        exec_function: Callable = partial(target_method_wrapper, target_method=target_method)
        res: list[T] = list(map_function(exec_function, parameters))

    return res


def process_pool_parallelize(target_method: Callable, parameters: list[dict[str, Any]], num_workers: int = 0, chunksize: int = 1, timeout: Optional[float] = None) -> list[T]:
    """
    ProcessPoolExecutor with the specification of the number of workers (default 0, meaning no parallelization).
    The parameter num_workers in this case is an int that must be in the range [-2, cpu_count]:
    - -2 means that number of workers is set to be equal to the total number of cores in your machine;
    - -1 means that number of workers is set to be equal to the total number of cores in your machine minus 1 (a single core remains free of work, so that the system is less likely to get frozen during the execution of the method);
    - 0 means that no parallelization is performed;
    - a strictly positive value means that the number of workers is set to be equal to the exact specified number which, of course, must not be higher than the available cores.
    Moreover, the chunksize parameter is provided, which corresponds to the chunksize parameter of the map method.
    """
    if num_workers < -2:
        raise AttributeError(f"Specified an invalid number of cores {num_workers}: this is a negative number lower than -2.")
    if num_workers > os.cpu_count():
        raise AttributeError(f"Specified a number of cores ({num_workers}) that is greater than the number of cores supported by your computer ({os.cpu_count()}).")
    
    if num_workers == 0:
        return [target_method(**t) for t in parameters]

    number_of_processes: int = {-2: (os.cpu_count()), -1: (os.cpu_count() - 1)}.get(num_workers, num_workers)
        
    with ProcessPoolExecutor(max_workers=number_of_processes) as executor:
        map_function: Callable = partial(executor.map, chunksize=chunksize, timeout=timeout)
        exec_function: Callable = partial(target_method_wrapper, target_method=target_method)
        res: list[T] = list(map_function(exec_function, parameters))

    return res


def multiprocessing_parallelize(target_method: Callable, parameters: list[dict[str, Any]], num_workers: int = 0, chunksize: int = 1, timeout: Optional[float] = None) -> list[T]:
    """
    Multiprocessing with the specification of the number of workers (default 0, meaning no parallelization).
    The parameter num_workers in this case is an int that must be in the range [-2, cpu_count]:
    - -2 means that number of workers is set to be equal to the total number of cores in your machine;
    - -1 means that number of workers is set to be equal to the total number of cores in your machine minus 1 (a single core remains free of work, so that the system is less likely to get frozen during the execution of the method);
    - 0 means that no parallelization is performed;
    - a strictly positive value means that the number of workers is set to be equal to the exact specified number which, of course, must not be higher than the available cores.
    Moreover, the chunksize parameter is provided, which corresponds to the chunksize parameter of the map method.
    """
    if num_workers < -2:
        raise AttributeError(f"Specified an invalid number of cores {num_workers}: this is a negative number lower than -2.")
    if num_workers > os.cpu_count():
        raise AttributeError(f"Specified a number of cores ({num_workers}) that is greater than the number of cores supported by your computer ({os.cpu_count()}).")
    
    if num_workers == 0:
        return [target_method(**t) for t in parameters]

    number_of_processes: int = {-2: (os.cpu_count()), -1: (os.cpu_count() - 1)}.get(num_workers, num_workers)
        
    with mp.Pool(processes=number_of_processes, maxtasksperchild=1) as pool:
        map_function: Callable = partial(pool.map, chunksize=chunksize, timeout=timeout)
        exec_function: Callable = partial(target_method_wrapper, target_method=target_method)
        res: list[T] = list(map_function(exec_function, parameters))

    return res


def target_method_wrapper(parameter: dict[str, Any], target_method: Callable) -> T:
    # This method is simply a wrapper that unpacks the provided input and calls the provided function with the unpacked input.
    # Since this method must be parallelized with map, it must be declared and implemented in the global scope of a Python script.
    return target_method(**parameter)

