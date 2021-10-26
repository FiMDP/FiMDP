from functools import reduce
from typing import List, TypeVar

T = TypeVar('T')


def power_set(original_set: List[T]) -> List[List[T]]:
    return reduce(lambda result, x: result + [subset + [x] for subset in result], original_set, [[]])


def power_set_names(original_names: List[str], lists_of_indices: List[List[int]]):
    if any(any([index >= len(original_names) for index in indices]) for indices in lists_of_indices):
        raise AttributeError(f"Incorrect indices, bigger than length of names.")
    return [[original_names[i] for i in index_set] for index_set in lists_of_indices]