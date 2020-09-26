"""
Find minimal capacity needed for given starting location
and target location.
"""

from .energy_solvers import BasicES
from .objectives import AS_REACH, BUCHI


def bin_search(mdp, init_loc, target_locs,
               starting_capacity=100,
               objective=BUCHI,
               max_starting_load=None
               ):
    """Search for min. capacity by brute-force using binary search.

    For given starting location (`init_loc`) and a set (iterable) of
    goal states (`target_locs`) in CMDP `mdp`, compute minimal capacity
    needed to fulfill the objective (Büchi by default) from the the
    starting location. Please not that giving more targets in target_locs
    means that we can choose 1 of them only and not visit the rest.

    The search starts from `capacity=100` by default. This can be
    changed by setting `starting_capacity`.

    If `max_starting_load` is given, don't consider capacities for
    which we need more than the given value from the starting
    location.

    The target_locs can be either an integer ID of a state or an
        `iterable` of those.

    Objective can be either `energy_solver.BUCHI` or `energy_solver.AS_REACH`.
        Default is `BUCHI`.
    """
    if isinstance(target_locs, int):
        target_locs = [target_locs]

    low = 1
    high = starting_capacity
    success = False

    while low < high:
        current_cap = (high + low) // 2
        solver = BasicES(mdp, current_cap, target_locs)
        # Get the results
        if objective == BUCHI:
            result = solver.get_min_levels(BUCHI)
        elif objective == AS_REACH:
            result = solver.get_min_levels(AS_REACH)
        else:
            raise ValueError("Objective not supported yet.")

        max_load = current_cap if max_starting_load is None else max_starting_load

        # capacity too low
        if result[init_loc] > max_load:
            low = current_cap + 1
        else:
            high = current_cap
            success = True

    if not success:
        raise ValueError(f"No capacity <= {starting_capacity} is enough.")

    return low