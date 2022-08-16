#!/usr/bin/env python3

import logging
import multiprocessing
import platform, psutil
import time
import sys
from functools import partial
from statistics import stdev
from typing import List, Tuple, Dict
from joblib import Parallel, delayed
import pickle

sys.path.append('/home/xnovot18/FiPOMDP')

from fimdp.core import ActionData
from fimdp.objectives import BUCHI
from fimdpenv.UUVEnv import SingleAgentEnv
from fipomdp import ConsPOMDP, log_utils
from fipomdp.energy_solvers import ConsPOMDPBasicES
from fipomdp.pomcp_20_sparse import OnlineStrategy
from fipomdp.environment_utils import set_cross_observations_to_UUV_grid
from fipomdp.pomcp_utils import matching_state_action, sample_from_distr

from fipomdp.rollout_functions import basic, grid_manhattan_distance, step_based


def uuv_experiment(computed_cpomdp: ConsPOMDP, computed_solver: ConsPOMDPBasicES, capacity: int, targets: List[int], random_seed: int, logger) -> \
        Tuple[int, bool, List[int], List[int], bool, int]:

    logger = logger

    # if computed_cpomdp.belief_supp_cmdp is None or computed_solver.bs_min_levels[BUCHI] is None:
    #     raise AttributeError(f"Given CPOMDP or its solver is not pre computed!")

# SPECIFY ROLLOUT FUNCTION from rollout_functions.py

    rollout_function = step_based
    #
    grid_adjusted = partial(grid_manhattan_distance, grid_size=[20, 20], targets=[103, 209, 210, 270])
    # rollout_function = grid_adjusted

# -----

#   HYPER PARAMETERS

    init_energy = capacity
    init_obs = 399
    init_bel_supp = tuple([399])
    exploration = 200
    rollout_horizon = 100
    max_iterations = 200
    actual_horizon = 100
    softmax_on = False

# -----

    strategy = OnlineStrategy(
        computed_cpomdp,
        capacity,
        init_energy,
        init_obs,
        init_bel_supp,
        targets,
        exploration,
        rollout_function,
        rollout_horizon=rollout_horizon,
        random_seed=random_seed,
        recompute=False,
        solver=computed_solver,
        logger=logger
    )

    simulated_state = init_bel_supp[0]

    reward = 0
    target_hit = False
    decision_times = []

    path = [simulated_state]

    for j in range(actual_horizon):
        pre_decision_time = time.time()
        action = strategy.next_action(max_iterations)
        simulated_state, new_obs = simulate_observation(computed_cpomdp, action, simulated_state)
        path.append(simulated_state)
        reward -= 1
        if simulated_state in targets:
            reward += 1000
            target_hit = True
            break

        strategy.update_obs(new_obs)
        decision_times.append(round(time.time() - pre_decision_time))

    logger.info(f"\n--------EXPERIMENT FINISHED---------")
    logger.info(f"--------RESULTS--------")

    logger.info(f"For max iterations: {max_iterations}, target has been reached {target_hit} times.")
    logger.info(f"Path of the agent was: {path}")
    logger.info(f"Decision times: {decision_times}")
    logger.info(f"Decision time average: {sum(decision_times) / len(decision_times)}, standard deviation: {stdev(decision_times)}")
    logger.info(f"Target hit: {target_hit}, reward: {reward}")

    return max_iterations, target_hit, path, decision_times, target_hit, reward


def simulate_observation(cpomdp: ConsPOMDP, bs_action: ActionData, src_state: int) -> Tuple[int, int]:
    cpomdp_action = matching_state_action(cpomdp, bs_action, src_state)
    new_state = sample_from_distr(cpomdp_action.distr)
    new_obs = sample_from_distr(cpomdp.get_state_obs_probs(new_state))
    return new_state, new_obs


def log_experiment_with_seed(cpomdp, env, i, log_file_name, solver, targets):
    handler = logging.FileHandler(f"./logs_20_sparse/{log_file_name}{i}.log", 'w')
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger(f"{i}")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(handler)
    logger.level = logging.INFO
    logger.info("START")
    uname = platform.uname()
    logger.info(f"Node name: {uname.node}")
    logger.info(f"System: {uname.system}")
    logger.info(f"Release: {uname.release}")
    logger.info(f"Version: {uname.version}")
    logger.info(f"Machine: {uname.machine}")
    logger.info(f"Processor: {uname.processor}")
    logger.info(f"RAM: {str(round(psutil.virtual_memory().total / (1024.0 ** 3)))} GB")
    return uuv_experiment(cpomdp, solver, env.capacities[0], targets, i, logger)


def main():
    log_file_name = "UUVExperimentsFromPythonFile_20_sparse"  # Change for your needs
    logging_level = logging.INFO
    # set to INFO (20) for logging to be active, set to DEBUG (10) for details,
    # set to 5 for extreme debug

    logging.basicConfig(
        filename=f"{log_file_name}.log",
        filemode="w",  # Erase previous log
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging_level,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    env = SingleAgentEnv(
        grid_size=[20, 20],
        capacity=20,
        reloads=[i*20+j for i in range(0, 20, 5) for j in range(0, 20, 5)],  # reloads in 5x5 grids
        targets=[103, 209, 210, 270],
        init_state=399,
        enhanced_actionspace=0,
    )

    mdp, targets = env.get_consmdp()
    mdp.__class__ = ConsPOMDP
    set_cross_observations_to_UUV_grid(mdp, (env.grid_size[0], env.grid_size[1]))

    cpomdp = mdp
    cpomdp.compute_guessing_cmdp_initial_state([399])

    with open("cpomdp_sparse", "wb") as cpomdp_file:
        pickle.dump(cpomdp, cpomdp_file)

    # with open("cpomdp_sparse", 'rb') as pickle_file:
    #    cpomdp = pickle.load(pickle_file)

    solver = ConsPOMDPBasicES(cpomdp, [399], env.capacities[0], targets)
    solver.compute_buchi()

    # with open("solver", "wb") as solver_file:
    #     pickle.dump(solver, solver_file)

    results = Parallel(n_jobs=23)(delayed(log_experiment_with_seed)(cpomdp, env, i, log_file_name, solver, targets) for i in range(100))

    logging.info(f"RESULTS (): {results}")

if __name__ == "__main__":
    main()
