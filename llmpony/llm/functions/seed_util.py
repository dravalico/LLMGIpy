import random
import numpy as np
import torch


def set_seeds(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def quadratic_seed(base_seed: int, offset_seed: int, multiply_by_prime_number: bool = True) -> int:
    return base_seed + (offset_seed * offset_seed) * (31 if multiply_by_prime_number else 1)


def cubic_seed(base_seed: int, offset_seed: int, multiply_by_prime_number: bool = True) -> int:
    return base_seed + (offset_seed * offset_seed * offset_seed) * (31 if multiply_by_prime_number else 1)
