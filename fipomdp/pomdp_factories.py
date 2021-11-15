from functools import reduce
from typing import List, TypeVar, Optional

T = TypeVar('T')


def power_set(original_set: List[T]) -> List[List[T]]:
    return reduce(lambda result, x: result + [subset + [x] for subset in result], original_set, [[]])


def power_set_names(original_names: List[str], lists_of_indices: List[List[int]]):
    if any(any([index >= len(original_names) for index in indices]) for indices in lists_of_indices):
        raise AttributeError(f"Incorrect indices, bigger than length of names.")
    return [[original_names[i] for i in index_set] for index_set in lists_of_indices]


def bel_supp_state_name(belief_supp: List[int]) -> str:
    if len(belief_supp) == 1:
        name = "bel_supp_" + str(belief_supp[0])
    else:
        name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", belief_supp)
    return name


def bel_supp_guess_state_name(belief_supp: List[int], guess: Optional[int]):
    if len(belief_supp) == 1:
        name = "bel_supp_" + str(belief_supp[0]) + "__guess" + str(guess)
    else:
        name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", belief_supp) + "__guess" + str(guess)
    return name
