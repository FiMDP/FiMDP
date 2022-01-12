#!/usr/bin/env python3

import logging
import platform, psutil
import math

from fimdpenv.UUVEnv import SingleAgentEnv
from fipomdp import ConsPOMDP
from fipomdp.pomcp import OnlineStrategy
from fipomdp.environment_utils import set_cross_observations_to_UUV_grid


def uuv_experiment():
    log_file_name = "UUVExperimentsFromPythonFile"  # Change for your needs
    logging_level = logging.INFO  # set to INFO for logging to be active

    logging.basicConfig(
        filename=f"{log_file_name}.log",
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
    capacity = env.capacities[0]
    init_energy = capacity
    init_obs = 399
    init_bel_supp = tuple([399])
    exploration = 0.9
    random_seed = 1

    cpomdp.compute_guessing_cmdp_initial_state([399])
    strategy = OnlineStrategy(
        cpomdp,
        capacity,
        init_energy,
        init_obs,
        init_bel_supp,
        targets,
        exploration,
        random_seed=random_seed,
        recompute=False,
    )

    strategy.next_action(1000)

    # different seed
    # for i in [200, 500, 1000]:  # max iterations
    #     for j in range(100):  # 100 actions
    #         action = strategy.next_action()
    #         cpomdp.actions_for_state(init_bel_supp[0])


def main():
    uuv_experiment()


if __name__ == "__main__":
    main()
