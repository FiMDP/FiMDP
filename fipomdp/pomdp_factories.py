from functools import reduce
from typing import List, TypeVar

T = TypeVar('T')


def power_set(original_set: List[T]) -> List[List[T]]:
    return reduce(lambda result, x: result + [subset + [x] for subset in result], original_set, [[]])

