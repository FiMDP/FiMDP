#!/usr/bin/env python3

import logging
import platform, psutil
from typing import List, Tuple, Dict

from fimdp.core import ActionData
from fimdp.objectives import BUCHI
from fimdpenv.UUVEnv import SingleAgentEnv
from fipomdp import ConsPOMDP
from fipomdp.energy_solvers import ConsPOMDPBasicES
from fipomdp.pomcp import OnlineStrategy
from fipomdp.environment_utils import set_cross_observations_to_UUV_grid
from fipomdp.pomcp_utils import matching_state_action, sample_from_distr


def uuv_experiment(computed_cpomdp: ConsPOMDP, computed_solver: ConsPOMDPBasicES, capacity: int, targets: List[int], random_seed: int) -> Dict[int, int]:

    if computed_cpomdp.belief_supp_cmdp is None or computed_solver.bs_min_levels[BUCHI] is None:
        raise AttributeError(f"Given CPOMDP or its solver is not pre computed!")

    init_energy = capacity
    init_obs = 399
    init_bel_supp = tuple([399])
    exploration = 0.9

    strategy = OnlineStrategy(
        computed_cpomdp,
        capacity,
        init_energy,
        init_obs,
        init_bel_supp,
        targets,
        exploration,
        random_seed=random_seed,
        recompute=False,
    )

    action = strategy.next_action(1000)

    simulated_state = init_bel_supp[0]

    max_iteration_target_reached_count = {200: 0, 500: 0, 1000: 0}

    for max_iterations in max_iteration_target_reached_count.keys():  # max iterations

        logging.info(f"\nLAUNCHING with max iterations: {max_iterations}\n")

        for j in range(100):  # 100 actions
            action = strategy.next_action(max_iterations)
            simulated_state, new_obs = simulate_observation(computed_cpomdp, action, simulated_state)
            if simulated_state in targets:
                max_iteration_target_reached_count[max_iterations] += 1
            strategy.update_obs(new_obs)

    logging.info(f"\n--------EXPERIMENT FINISHED---------")
    logging.info(f"--------RESULTS--------")
    for k, v in max_iteration_target_reached_count.items():
        logging.info(f"For max iterations: {k}, target has been reached {v} times.")

    return max_iteration_target_reached_count


def simulate_observation(cpomdp: ConsPOMDP, bs_action: ActionData, src_state: int) -> Tuple[int, int]:
    cpomdp_action = matching_state_action(src_state, bs_action)
    new_state = sample_from_distr(cpomdp_action.distr)
    new_obs = sample_from_distr(cpomdp.get_state_obs_probs(new_state))
    return new_state, new_obs


def main():
    log_file_name = "UUVExperimentsFromPythonFileDEBUG"  # Change for your needs
    logging_level = logging.DEBUG  # set to INFO for logging to be active, set to DEBUG for details

    env = SingleAgentEnv(
        grid_size=[20, 20],
        capacity=20,
        reloads=[64, 69, 74, 164, 169, 174, 264, 269, 274, 364, 369, 374],
        targets=[103, 209, 210, 270],
        init_state=399,
        enhanced_actionspace=0,
    )

    mdp, targets = env.get_consmdp()
    mdp.__class__ = ConsPOMDP
    set_cross_observations_to_UUV_grid(mdp, (env.grid_size[0], env.grid_size[1]))

    logging.info("Environment created")

    cpomdp = mdp
    cpomdp.compute_guessing_cmdp_initial_state([399])

    solver = ConsPOMDPBasicES(cpomdp, [399], env.capacities[0], targets)
    solver.compute_buchi()

    for i in range(1):
        logging.basicConfig(
            filename=f"{log_file_name}{i}.log",
            filemode="w",  # Erase previous log
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging_level,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.info("START")

        uname = platform.uname()
        logging.info(f"Node name: {uname.node}")
        logging.info(f"System: {uname.system}")
        logging.info(f"Release: {uname.release}")
        logging.info(f"Version: {uname.version}")
        logging.info(f"Machine: {uname.machine}")
        logging.info(f"Processor: {uname.processor}")
        logging.info(f"RAM: {str(round(psutil.virtual_memory().total / (1024.0 ** 3)))} GB")

        logging.info("Creating UUV environment with observations.")

        uuv_experiment(cpomdp, solver, env.capacities[0], targets, i)


if __name__ == "__main__":
    main()
