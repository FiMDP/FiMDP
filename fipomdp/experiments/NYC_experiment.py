#!/usr/bin/env python3
import logging
import platform
from typing import List, Tuple, Dict

import psutil
from joblib import Parallel, delayed

from fimdp.objectives import BUCHI
from fipomdp import ConsPOMDP
from fipomdp.energy_solvers import ConsPOMDPBasicES
from fipomdp.experiments.NYC_environment import NYCPOMDPEnvironment
from fipomdp.experiments.UUV_experiment import simulate_observation
from fipomdp.pomcp import OnlineStrategy

from fipomdp.rollout_functions import basic, grid_manhattan_distance


def nyc_experiment(computed_cpomdp: ConsPOMDP, computed_solver: ConsPOMDPBasicES, capacity: int, targets: List[int], random_seed: int, logger) -> \
Tuple[Dict[int, int], List[int]]:
    logger = logger

    if computed_cpomdp.belief_supp_cmdp is None or computed_solver.bs_min_levels[BUCHI] is None:
        raise AttributeError(f"Given CPOMDP or its solver is not pre computed!")

    init_energy = capacity
    init_obs = computed_cpomdp.state_with_name('42459137')
    init_bel_supp = tuple([computed_cpomdp.state_with_name('42459137')])
    exploration = 1
    rollout_horizon = 100

# SPECIFY ROLLOUT FUNCTION

    rollout_function = basic

    # grid_adjusted = partial(grid_manhattan_distance, grid_size=[..., ...], targets=[...])
    # rollout_function = grid_adjusted

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

    path = [simulated_state]

    max_iteration_target_reached_count = {1000: 0}

    for max_iterations in max_iteration_target_reached_count.keys():  # max iterations

        logger.info(f"\nLAUNCHING with max iterations: {max_iterations}\n")

        for j in range(100):  # 100 actions
            action = strategy.next_action(max_iterations)
            simulated_state, new_obs = simulate_observation(computed_cpomdp, action, simulated_state)
            path.append(simulated_state)
            if simulated_state in targets:
                max_iteration_target_reached_count[max_iterations] += 1
            strategy.update_obs(new_obs)

    logger.info(f"\n--------EXPERIMENT FINISHED---------")
    logger.info(f"--------RESULTS--------")
    for k, v in max_iteration_target_reached_count.items():
        logger.info(f"For max iterations: {k}, target has been reached {v} times.")
        logger.info(f"Path of the agent was: {path}")

    return max_iteration_target_reached_count, path


def log_experiment_with_seed(cpomdp, env, i, log_file_name, solver, targets):
    handler = logging.FileHandler(f"./logs/{log_file_name}{i}.log", 'w')
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
    return nyc_experiment(cpomdp, solver, env.cmdp_env.capacity, targets, i, logger)


def main():
    log_file_name = "NYCExperiments"  # Change for your needs
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

    env = NYCPOMDPEnvironment()
    cpomdp, targets = env.get_cpomdp()

    cpomdp.compute_guessing_cmdp_initial_state([cpomdp.state_with_name('42459137')])

    solver = ConsPOMDPBasicES(cpomdp, [cpomdp.state_with_name('42459137')], env.cmdp_env.capacity, targets)
    solver.compute_buchi()

    results = Parallel(n_jobs=10)(
        delayed(log_experiment_with_seed)(cpomdp, env, i, log_file_name, solver, targets) for i in range(10))

    logging.info(f"RESULTS (): {results}")


if __name__ == "__main__":
    main()

