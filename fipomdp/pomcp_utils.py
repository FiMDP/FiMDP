import random
from typing import Tuple, List, Dict

from fimdp.core import ActionData
from fipomdp import ConsPOMDP


def filter_safe_actions(
    action_shield: List[Tuple[int, ActionData]], energy: int, bel_supp_state: int
) -> List[ActionData]:
    """Utility function to filter actions according to required energy for them with given action shield.

    Parameters
    ----------
    action_shield : List[Tuple[int, ActionData]]
        List of pairs of minimum energy and action for which it is required.
    energy : int
        Available energy.
    bel_supp_state : int
        State in belief support cmdp to filter actions by.

    Returns
    -------
    List[ActionData]
        List of available actions for given energy and given belief support cmdp state.

    """
    return [
        action
        for min_energy, action in action_shield
        if min_energy <= energy and action.src == bel_supp_state
    ]


def sample_from_distr(distribution: Dict[int, float]) -> int:
    """Utility function for sampling from distribution.

    Parameters
    ----------
    distribution : Dict[int, float]

    Returns
    -------
    int
        Sampled int key weighted by float values

    """
    keys = list(distribution.keys())
    values = list(distribution.values())
    return random.choices(population=keys, weights=values, k=1)[0]


def matching_state_action(
    cpomdp: ConsPOMDP, bs_action: ActionData, state: int
) -> ActionData:
    """Utility function for finding matching cpomdp action from its belief support cmdp action, with given state.

    Parameters
    ----------
    cpomdp : ConsPOMDP
        cpomdp with action space to search.
    bs_action : ActionData
        Action in belief support CMDP in given cpomdp.
    state : int
        State to match the action with.

    Returns
    -------
    ActionData
        Matching action with given state as source.
    """
    for act in cpomdp.actions_for_state(state):
        if act.label == bs_action.label:
            return act

    raise ValueError(f"State {state} has no action labeled {bs_action.label}")
