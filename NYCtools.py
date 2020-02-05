# -*- coding: utf-8 -*-
"""
Description:

Author: Pranay Thangeda
License: MIT License
Email: contact@prny.me
Description: Collection of tools for working on the NYC example.
"""

import timeit
import json
import numpy as np
import pandas as pd
import networkx as nx
from energy_solver import *
import matplotlib.pyplot as plt

# Function for evaluating compute time of Buchi objective for different target sets
def timeit_difftargets(m, cap, set_size = 100, num_tests = 1):

    compute_time = np.empty(num_tests)
    for i in range(num_tests):
        targets = np.random.randint(0, high=m.num_states, size=(set_size))
        def calc_time():
            s = EnergySolver(m, cap=cap, targets=targets)
            s.get_strategy(BUCHI, recompute=True)
        num_compute = 10
        compute_time[i] = timeit.timeit(calc_time, number=num_compute)/num_compute

    plt.hist(compute_time, density=True, facecolor='b')

    plt.xlabel('Compute Time (sec)')
    plt.ylabel('Probability')
    plt.title('Histogram of Buchi Objective Compute Time')
    plt.grid(True)
    plt.show()
    mean = np.mean(compute_time)
    sd = np.std(compute_time)
    return (mean, sd)


# Function for visualizing the Strategies of the agent
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