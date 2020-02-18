"""
Benchmarking and visualization tools for AEV in NYC case study.
"""

import timeit
import json
import ch_parser
import numpy as np
from energy_solver import *

def timeit_difftargets(m, cap, target_size = 100, num_samples = 100, num_tests=5, obj=BUCHI):

    """Returns a list of compute times for given objective for the NYC AEV
        problem with varying target sets.

    Parameters
    ----------
    m : mdp;  object of class ConsMDP.
       A valid Markov Decision Process.

    cap : positive integer.
       The energy capacity of the agent.

    target_size : positive integer, optional
       Size of the set of random targets to be generated for calculating the
       compute time variation. Takes a default value of 100.

    num_samples : positive integer, optional
       Number of times a random target set is generated and it's compute time
       for any given objective is calculated. Takes a default of 100.

    num_tests : positive integer, optional
       Number of times the compute time is calculated using timeit for each
       individual test. Takes a default value of 5.

    obj : one of MIN_INIT_CONS, SAFE, POS_REACH, AS_REACH, BUCHI, optional
       Objective for which the compute times are calculated. Takes BUCHI as
       the default value.

    Returns
    -------
    comptime : array_like
       List of computational times for different target sets.

    Examples
    --------
    >>> m, targets = ch_parser.parse('NYCstreetnetwork.json')
    >>> comptime = timeit_difftargets(m, cap=200, target_size=100)

    Notes
    -----
    The values of timings returned might signficantly vary depending on the
    machine configuration and the target states set.

    """

    comptime = np.empty(num_samples)
    for i in range(num_samples):
        targets = np.random.randint(0, high=m.num_states, size=(target_size))
        def calc_time():
            s = EnergySolver(m, cap=cap, targets=targets)
            s.get_strategy(obj, recompute=True)
        comptime[i] = timeit.timeit(calc_time, number=num_tests)/num_tests
    return comptime


def timeit_diffcaps(m, targets, cap_bound , num_samples = 100, num_tests=10, obj=BUCHI):

    """Returns a list of tuples where each tuple consists of the energy capacity
    and its corresponding computational time for a given objective and target
    set in the NYC AEV problem.

    Parameters
    ----------
    m : mdp;  object of class ConsMDP.
       A valid Markov Decision Process.

    targets : array_like, list of target states
       A list containing all the target states.

    cap_bound : positive integer.
       Upper bound of the interval specifying the allowed energy capacity
       for the agent.

    num_samples : positive integer, optional
       Number of equally spaced samples to be collected from the interval
       [0, cap_bound] for evaluation of their computational time. Takes a
       default value of 100.

    num_tests : positive integer, optional
       Number of times the compute time is calculated using timeit for each
       sampled capacity value. Takes a default value of 10.

    obj : one of MIN_INIT_CONS, SAFE, POS_REACH, AS_REACH, BUCHI, optional
       Objective for which the compute times are calculated. Takes BUCHI as
       the default value.

    Returns
    -------
    comptime : array_like
       List with tuples of capacity and expected computational time for a fixed
       set of targets

    Examples
    --------
    >>> m, targets = ch_parser.parse('NYCstreetnetwork.json')
    >>> comptime = timeit_diffcaps(m, targets=targets, cap_bound=200, obj=BUCHI)

    Notes
    -----
    The values of timings returned might signficantly vary depending on the
    machine configuration.

    """

    comptime = []

    cap_list = np.linspace(1,cap_bound, num_samples)
    for i in range(num_samples):
        def calc_time():
            s = EnergySolver(m, cap=cap_list[i], targets=targets)
            s.get_strategy(obj, recompute=True)
        comptime.append((cap_list[i], timeit.timeit(calc_time, number=num_tests)/num_tests))
    return comptime


def visualize_strategy(strategy, m, starting_state, targets):

    # Create policy array with state-action mapping
    policy = {s:None for s in range(m.num_states)}
    empty_count = 0
    for index in range(m.num_states):
        action_dict = strategy[index]
        if bool(action_dict):
            min_item = min(action_dict.items(), key=lambda x: x[0])
            policy[index] = min_item[1]
        else:
            empty_count += 1

    if empty_count != 0:
        raise Exception('Not all states have an action specified by the policy')

    # Translate policy to old state labeling notation
    policy_beta = {}
    state_map = m.state_labels
    for index in range(m.num_states):
        policy_beta.update({state_map[index]: policy[index]})

    # Resultant State in NYC graph for any action
    dynamics = {}
    with open('NYCstreetnetwork.json','r') as f:
        raw_data = json.load(f)
        for edge in raw_data["edges"]:
            tail = edge["tail"]
            head = edge["head"]
            if tail[:2] == 'pa':
                action_label = tail[4:]
                dynamics.update({action_label:head})

    # Set of targets
    targets_beta = []
    for item in targets:
        targets_beta.append(state_map[item])

    # Follow policy and maintain history
    num_targets = len(targets_beta)
    history = [starting_state]
    current_state = starting_state

    while True:
        current_action = policy_beta[current_state]
        next_state = dynamics[current_action]
        current_state = next_state
        history.append(current_state)

        if len(targets_beta.intersection(set(history))) == num_targets:
            break
            rt.visualize_route(history, targets_beta)


if __name__ == '__main__':

    m, targets = ch_parser.parse('NYCstreetnetwork.json')
 #   comptime_dt = timeit_difftargets(m, cap=200, target_size = 100, num_samples=100, obj=BUCHI)
    comptime_dc = timeit_diffcaps(m, targets, cap_bound = 100, num_samples = 20, num_tests=10, obj=BUCHI)






