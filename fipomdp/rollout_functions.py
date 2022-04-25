from typing import Tuple, List


def basic(state: int, steps: int, consumed_energy: int, reload_count: int, remaining_energy: int,
          target_found: bool) -> float:
    return 1 if target_found else 0.1


def step_based(state: int, steps: int, consumed_energy: int, reload_count: int, remaining_energy: int,
               target_found: bool) -> float:
    return -steps if target_found else -2 * steps


def consumption_based(state: int, steps: int, consumed_energy: int, reload_count: int, remaining_energy: int,
                      target_found: bool) -> float:
    return 1000 - consumed_energy + remaining_energy + 0.5 if target_found else - consumed_energy + remaining_energy


def grid_manhattan_distance(state: int, steps: int, consumed_energy: int, reload_count: int, remaining_energy: int,
                            target_found: bool, grid_size: Tuple[int, int], targets: List[int]) -> float:
    if target_found:
        return -steps
    else:
        x_dists = [abs(state / grid_size[0] - target / grid_size[0]) for target in targets]
        y_dists = [abs(state % grid_size[0] - target % grid_size[0]) for target in targets]

        return -steps - min(x_dists[i] + y_dists[i] for i in range(len(x_dists)))


def tiger_step_based(state: int, steps: int, consumed_energy: int, reload_count: int, remaining_energy: int, target_found: bool, tiger_bite_weight: int) -> float:
    if not target_found:
        return -steps
    if state == 6:
        behind_the_door = -20 * tiger_bite_weight
    else:
        behind_the_door = 20
    return -steps + behind_the_door


def product(state: int, steps: int, consumed_energy: int, reload_count: int, remaining_energy: int, target_found:bool,
            a: int, b: int) -> float:
    return a * b
