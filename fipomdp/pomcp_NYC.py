"""Module defining an Online Strategy using POMCP algorithm modified with shielding.

Classes used for POMCP:
 * POMCPTree - represents the tree with root, parameters needed to reset it,
                and methods for monte carlo iterations, rollouts and rollout evalutation functions,
                 node updates, and picking the best action.
 * POMCPNode - abstract node representation with common functionality of action and history nodes,
                as in a visiting method.
 * POMCPActionNode - tree node representing action with history nodes as children and functionality for sampling of nodes.
 * POMCPHistoryNode - tree node representing history with action nodes as children, UCT selector of child action nodes,
                storing full history of the previously traversed history and action nodes from tree root.


It contains an interface for the strategy, similar to strategies in FiMDP for CMDPs.
Classes used for Strategy:
 * OnlineStrategy - has three interface components: picking action, updating observations and resetting.
"""

from __future__ import annotations

import math
import random
from copy import copy
from typing import List, Tuple, Dict, Optional, Callable

from fimdp.core import ActionData
from fimdp.distribution import uniform
from fipomdp import ConsPOMDP, log_utils
from fipomdp.energy_solvers import ConsPOMDPBasicES

import logging

from fipomdp.environment_utils import softmax
from fipomdp.pomcp_utils import sample_from_distr, filter_safe_actions, matching_state_action


class POMCPTree:
    """POMCP tree representation, with shielded actions.

    This tree representation uses only the root of the tree, rest of the tree is accessible through nodes themselves
    """

    root: POMCPHistoryNode
    cpomdp: ConsPOMDP
    targets: List[int]
    iterations: int
    capacity: int
    action_shield: Dict[int, Dict[ActionData, int]]
    exploration: float
    rollout_horizon: int
    rollout_function: Callable[[int, int, int, int, int, bool], float]
    random_seed: int
    max_function: Callable[[List[float]], float]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        targets: List[int],
        root_obs: int,
        root_bel_supp: Tuple[int, ...],
        capacity: int,
        energy: int,
        action_shield: Dict[int, Dict[ActionData, int]],
        exploration: float,
        random_seed: int,
        rollout_function: Callable[[int, int, int, int, int, bool], float],
        rollout_horizon: int = 100,
        root_belief: Optional[Dict[int, float]] = None,
        logger=None,
        softmax_on: bool = False
    ):
        if logger is None:
            logger = log_utils.get_logger_for_seed(random_seed)

        logger.info(
            f"Constructing tree, parameters: \n"
            f"targets: {targets},\n"
            f"root observation: {root_obs},\n"
            f"root belief support: {root_bel_supp},\n"
            f"capacity: {capacity},\n"
            f"energy: {energy},\n"
            f"exploration: {exploration},\n"
            f"random seed: {random_seed},\n"
            f"rollout horizon: {rollout_horizon},\n"
            f"rollout function: {rollout_function},\n"
            f"root belief: {root_belief}"
        )

        self.cpomdp = cpomdp
        self.targets = targets
        self.iterations = 0
        self.capacity = capacity
        self.action_shield = action_shield
        self.exploration = exploration
        self.rollout_horizon = rollout_horizon
        self.rollout_function = rollout_function

        if root_belief is None:
            root_belief = {
                k: v
                for k, v in uniform(self.cpomdp.get_obs_states(root_obs)).items()
                if k in root_bel_supp
            }

        self.logger = logger

        if softmax_on:
            self.max_function = softmax
        else:
            self.max_function = max

        self.root = POMCPHistoryNode(
            cpomdp,
            self.capacity,
            root_obs,
            root_bel_supp,
            energy,
            exploration,
            [],
            action_shield,
            self.max_function,
            root_belief,
            logger
        )

        self.random_seed = random_seed
        random.seed(
            random_seed
        )  # Over the scope of the tree instance, and all the node instances in it

        logger.info(f"Tree created")

    def iteration(self, sampled_state: int) -> Tuple[POMCPHistoryNode, List[int]]:
        """Method for simulating one iteration of POMCP algorithm.

        Traverses the tree downwards and when it reaches leaf node, picks action one last time and returns the newly
        created history node, along with accumulated particles along the way.

        Returns
        -------
        Tuple[POMCPHistoryNode, List[int]]
            Pair of the newest history node and particles to update the tree with.

        """
        current_history_node = self.root
        belief_particles = []
        tmp_sample = sampled_state
        while current_history_node.visits != 0 and tmp_sample not in self.targets:
            node, belief = current_history_node.simulate_action(tmp_sample)
            current_history_node = node
            belief_particles.append(belief)
            tmp_sample = belief

        self.iterations += 1

        self.logger.debug(f"--------ITERATION: {self.iterations}---------")
        self.logger.debug(f"--------BELIEF_PARTICLES: {belief_particles}--------")

        return current_history_node, belief_particles

    def update_tree(
        self, history_node: POMCPHistoryNode, result: float, belief_particles: List[int]
    ) -> None:
        """Method for simulating one tree update for given leaf node, by visiting each node of its history,
        and updating it with given result of rollout evaluation, and for history nodes also with particles accumulated.

        Parameters
        ----------
        history_node : POMCPHistoryNode
            Given leaf node.
        result : float
            Given rollout result.
        belief_particles : List[int]
            Given belief particles.
        """
        history = history_node.history

        if len(history) != len(belief_particles):
            raise AttributeError(
                f"Incorrect parameters: history with length {len(history)} has different length than belief particles: {len(belief_particles)}."
            )

        for i in range(len(history)):
            history[i][0].visit(result)
            history[i][1].visit(result)
            if i == 0:
                continue
            history[i][0].bel_particle_filter[belief_particles[i - 1]] += 1

        history_node.visit(result)

        if len(belief_particles) != 0:  # if not root rollout update
            history_node.bel_particle_filter[belief_particles[-1]] += 1

    def tree_run(self, max_iterations: int) -> None:

        """Method for simulating one full tree run, with all iterations, rollouts and updates.

        Parameters
        ----------
        max_iterations: int
            Number of max iterations.
        """

        self.logger.info(f"Launching tree run with {max_iterations} iterations")

        for i in range(max_iterations):

            sampled_state = sample_from_distr(self.root.belief)

            self.logger.info(
                f"Launching tree iteration and rollout with sampled state {sampled_state}."
            )

            iter_hist_node, iter_beliefs = self.iteration(sampled_state)

            if len(iter_beliefs) == 0:
                result = self.rollout(
                    iter_hist_node, sampled_state, self.rollout_horizon - len(iter_hist_node.history)
                )
            else:
                result = self.rollout(
                    iter_hist_node, iter_beliefs[-1], self.rollout_horizon - len(iter_hist_node.history)
                )

            self.update_tree(iter_hist_node, result, iter_beliefs)

            self.logger.info(
                f"Tree iteration finished, new history node has observation {iter_hist_node.obs} and belief support {iter_hist_node.bel_supp}"
            )
            self.logger.info(f"Rollout of this node has been evaluated as {result}")

        self.logger.info(f"Tree run finished")

    def tree_reset(
        self,
        energy: int,
        obs: int,
        bel_supp: Tuple[int, ...],
        belief: Dict[int, float],
        exploration: float,
        random_seed: int,
    ) -> None:
        """Method for resetting the tree with new initial conditions.

        Parameters
        ----------
        energy : int
        obs : int
        bel_supp : Tuple[int, ...]
        exploration : float
        random_seed : int
        belief : Dict[int, float]
        """

        self.logger.info(
            f"Resetting the tree with new root node, parameters:"
            f"observation: {obs},\n"
            f"belief support: {bel_supp},\n"
            f"energy: {energy},\n"
            f"exploration: {exploration},\n"
            f"random seed: {random_seed},\n"
            f"root belief: {belief}"
        )

        self.root = POMCPHistoryNode(
            self.cpomdp,
            self.capacity,
            obs,
            bel_supp,
            energy,
            exploration,
            [],
            self.action_shield,
            self.max_function,
            belief,
            logger=self.logger
        )

        self.iterations = 0
        self.random_seed = random_seed
        random.seed(random_seed)
        self.logger = log_utils.get_logger_for_seed(random_seed)

        self.logger.info(f"Finished tree reset")

    def best_action(self, max_iterations: int) -> ActionData:
        """Method for picking the best action of this tree instance.
        (Should be called after a tree run)

        Parameters
        ----------
        max_iterations : int
            Number of all iterations.

        Returns
        -------
        ActionData
            Selected action.
        """

        self.logger.info(f"Picking best action from tree")

        self.tree_run(max_iterations)
        uct_values = [act_node.avg_val for act_node in self.root.children]
        best_action_indices = [
            uct_values.index(i) for i in uct_values if i == max(uct_values)
        ]

        action_node = self.root.children[random.sample(best_action_indices, 1)[0]]
        action = action_node.bel_supp_action

        for act_node in self.root.children:
            f"{act_node.bel_supp_action} action was evaluated with value of {act_node.avg_val}"

        self.logger.info(
            f"{action} action was evaluated highest with value of {action_node.avg_val}"
        )

        return action

    def rollout(
        self, history_node: POMCPHistoryNode, state: int, horizon: int
    ) -> float:
        """Rollout method for given history node, state and rollout horizon.
        Simulates uniform safe action continuation and returns number of steps needed to reach a target,
        in case of not finding the target return double horizon value.

        Parameters
        ----------
        history_node : POMCPHistoryNode
        state : int
        horizon : int

        Returns
        -------
        float
            Rollout evaluation of the node.
        """
        target_found = False
        steps = 0
        energy = history_node.energy
        bel_supp_state = history_node.bel_supp_state

        if state in self.targets:
            return 0

        safe_actions = filter_safe_actions(self.action_shield, energy, bel_supp_state)
        sampled_state = state

        consumed_energy = 0
        reload_count = 0

        for i in range(horizon):
            if len(safe_actions) == 0:
                return 1000 * horizon * (-1)
            bs_action = random.sample(safe_actions, 1)[0]
            state_action = matching_state_action(self.cpomdp, bs_action, sampled_state)
            energy -= state_action.cons
            consumed_energy += state_action.cons
            steps += 1
            new_state = sample_from_distr(state_action.distr)

            if self.cpomdp.is_reload(new_state):
                energy = self.capacity
                reload_count += 1

            if new_state in self.targets:
                target_found = True
                break

            sampled_state = new_state
            new_bel_supps = [
                self.cpomdp.belief_supp_cmdp.bel_supps[i] for i in bs_action.distr
            ]

            obs_distr = self.cpomdp.get_state_obs_probs(sampled_state)
            bel_supp = ()

            while len(obs_distr) > 0 and bel_supp == ():
                dest_obs = sample_from_distr(obs_distr)
                dest_obs_states = self.cpomdp.get_obs_states(dest_obs)

                possible_bel_supps = []

                for b_s in new_bel_supps:
                    if sampled_state in b_s and all(elem in dest_obs_states for elem in b_s):
                        possible_bel_supps.append(b_s)

                if len(possible_bel_supps) > 0:
                    bel_supp = max(possible_bel_supps, key=lambda x: len(x))
                    break

                obs_distr.pop(dest_obs)

            bel_supp_state = self.cpomdp.belief_supp_cmdp.bel_supp_indexer[
                tuple(bel_supp)
            ]

            safe_actions = filter_safe_actions(
                self.action_shield, energy, bel_supp_state
            )

        return self.rollout_function(sampled_state, steps, consumed_energy, reload_count, energy, target_found)

    def use_outcome(self, action: ActionData, outcome: int):
        """Method for using new observation from previously selected (best) action
         to reset the tree after one tree run.

        Parameters
        ----------
        action : ActionData
            Previously selected action
        outcome : int
            New observation received
        """

        self.logger.info(f"Updating the tree with observation {outcome}")

        new_history_node = None
        for action_node in self.root.children:
            if action_node.bel_supp_action == action:
                for history_node in action_node.children:
                    if history_node.obs == outcome:
                        new_history_node = history_node
                        break
                break

        if new_history_node is None:

            belief_supps = [self.cpomdp.belief_supp_cmdp.bel_supps[i] for i in action.distr.keys()]

            new_energy = self.root.energy - action.cons
            new_bel_supp = ()

            obs_states = self.cpomdp.get_obs_states(outcome)

            for b_s in belief_supps:
                if len(b_s) > len(new_bel_supp) and all(elem in obs_states for elem in b_s):
                    new_bel_supp = b_s

            if len(new_bel_supp) == 0:
                raise ValueError(
                    f"Error, new history node not found according to observation."
                )

            new_particle_filter = uniform(new_bel_supp)

        else:
            new_energy = new_history_node.energy
            new_bel_supp = new_history_node.bel_supp
            new_particle_filter = new_history_node.bel_particle_filter

        self.tree_reset(
            new_energy,
            outcome,
            tuple(new_bel_supp),
            new_particle_filter,
            self.exploration,
            self.random_seed,
        )

        self.logger.info(f"New sampled node to fit observation was created")


class POMCPNode:
    """Class for abstract functionality of both types of nodes in POMCPTree.
    Supports only visits.

    Attributes
    ---------
    visits : int
        Number of visits in this node.
    avg_val : float
        Current value of this node.
    """

    cpomdp: ConsPOMDP
    visits: int
    avg_val: float

    def __init__(self, cpomdp: ConsPOMDP):
        self.cpomdp = cpomdp
        self.visits = 0
        self.avg_val = 0

    def visit(self, value: float) -> None:
        """Method for visiting this node and update its value average.

        Parameters
        ----------
        value : float
            New value for update.
        """
        self.avg_val = (self.avg_val * self.visits + value) / (self.visits + 1)
        self.visits += 1


class POMCPActionNode(POMCPNode):
    """Class representing Action nodes of POMCPTree. Supports sampling of new history node.

    Attributes
    ---------
    parent_node : POMCPHistoryNode
        Parent history node.
    bel_supp_action : ActionData
        This node's action.
    children : List[POMCPHistoryNode]
        List of child history nodes.
    """

    parent_node: POMCPHistoryNode
    bel_supp_action: ActionData
    children: List[POMCPHistoryNode]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        parent_node: POMCPHistoryNode,
        bel_supp_action: ActionData,
        logger=None
    ):
        if logger is None:
            logger = logging.getLogger()
        super(POMCPActionNode, self).__init__(cpomdp)
        self.parent_node = parent_node
        self.bel_supp_action = bel_supp_action
        self.children = []
        self.logger = logger

    def sample_hist_node(self, state: int) -> Tuple[POMCPHistoryNode, int]:
        """Method for sampling history node and state from this action node with given state sample from parent node.

        Finds matching action to this node's belief supp cmdp action with given state and samples from this
        matched action's distribution.

        Parameters
        ----------
        state : int
            Given parent node sampled state.

        Returns
        -------
        Tuple[POMCPHistoryNode, int]
            Pair of new node and new sampled state

        """
        cpomdp_state_action = matching_state_action(
            self.cpomdp, self.bel_supp_action, state
        )

        cpomdp_state_action_distr = copy(cpomdp_state_action.distr)

        bel_supp_dest_states = self.bel_supp_action.get_succs()
        belief_supps = [
            tuple(self.cpomdp.belief_supp_cmdp.bel_supps[bel_supp_state])
            for bel_supp_state in bel_supp_dest_states
        ]

        self.logger.debug("--------")
        self.logger.debug(f"ALL BELIEF SUPPS: {belief_supps}")
        self.logger.debug(
            f"BELIEF SUPP ACTION: {self.bel_supp_action}, SRC BELIEF: {self.cpomdp.belief_supp_cmdp.bel_supps[self.bel_supp_action.src]}"
        )

        timeout = 0
        belief_supp = ()

        while (
            belief_supp == () and timeout < 1000 and len(cpomdp_state_action_distr) > 0
        ):
            dest_state = sample_from_distr(cpomdp_state_action_distr)
            obs_distr = self.cpomdp.get_state_obs_probs(dest_state)

            self.logger.debug(f"OBS_DISTR: {obs_distr}")
            self.logger.debug(f"MATCHING STATE ACTION: {cpomdp_state_action}")

            while len(obs_distr) > 0 and belief_supp == ():
                dest_obs = sample_from_distr(obs_distr)
                dest_obs_states = self.cpomdp.get_obs_states(dest_obs)

                possible_bel_supps = []

                for b_s in belief_supps:
                    if dest_state in b_s and all(elem in dest_obs_states for elem in b_s):
                        possible_bel_supps.append(b_s)

                if len(possible_bel_supps) > 0:
                    belief_supp = max(possible_bel_supps, key=lambda x: len(x))
                    break

                obs_distr.pop(dest_obs)

            if dest_state not in belief_supp:
                belief_supp = ()
                cpomdp_state_action_distr.pop(dest_state)

        if belief_supp == ():
            self.logger.debug("FATAL ERROR coming up")
            self.logger.debug(
                f"SRC_STATE: {state}, DEST STATE: {dest_state}, OBS: {dest_obs}, DEST BELIEF_SUPP: {belief_supps}"
            )
            raise ValueError(
                f"Couldn't match observation, for belief_supps: {belief_supps} and state: {dest_state}"
            )

        self.logger.debug(f"PICKED BELIEF SUPP: {belief_supp}")

        for hist_node in self.children:
            if hist_node.obs == dest_obs and hist_node.bel_supp == belief_supp:
                return hist_node, dest_state

        new_energy = (
            self.parent_node.capacity
            if dest_state in self.cpomdp.reloads
            else self.parent_node.energy - self.bel_supp_action.cons
        )

        new_hist = copy(self.parent_node.history)
        new_hist.append((self.parent_node, self))
        new_child = POMCPHistoryNode(
            self.cpomdp,
            self.parent_node.capacity,
            dest_obs,
            belief_supp,
            new_energy,
            self.parent_node.exploration,
            new_hist,
            self.parent_node.action_shield,
            self.parent_node.max_function,
            logger=self.parent_node.logger
        )
        self.children.append(new_child)

        return new_child, dest_state


class POMCPHistoryNode(POMCPNode):
    """Class representing history nodes of POMCPTree.
    Creates action nodes during construction of this node.

    Has methods for UCT calculation and simulating current best action.

    Attributes
    ---------
    cpomdp : ConsPOMDP
    children : List[POMCPActionNode]
        List of child action nodes.
    obs : int
    bel_supp : Tuple[int, ...]
    bel_particle_filter: Dict[int, int]
    energy : int
    exploration : float
    history : List[Tuple[POMCPHistoryNode, POMCPActionNode]]
    action_shield : List[Tuple[int, ActionData]]

    """

    cpomdp: ConsPOMDP
    capacity: int
    children: List[POMCPActionNode]
    obs: int
    bel_supp: Tuple[int, ...]
    belief: Dict[int, float]
    bel_particle_filter: Dict[int, int]
    energy: int
    exploration: float
    history: List[Tuple[POMCPHistoryNode, POMCPActionNode]]
    action_shield: Dict[int, Dict[ActionData, int]]
    max_function: Callable[[List[float]], float]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        capacity: int,
        obs: int,
        bel_supp: Tuple[int, ...],
        energy: int,
        exploration: float,
        history: List[Tuple[POMCPHistoryNode, POMCPActionNode]],
        action_shield: Dict[int, Dict[ActionData, int]],
        max_function: Callable[[List[float]], float],
        belief: Optional[Dict[int, float]] = None,
        logger = None,
    ) -> None:
        super(POMCPHistoryNode, self).__init__(cpomdp)
        if belief is None:
            belief = {}
        if logger is None:
            logger = logging.getLogger()
        self.capacity = capacity
        self.children = []
        self.obs = obs
        self.bel_supp = bel_supp
        self.bel_supp_state = cpomdp.belief_supp_cmdp.bel_supp_indexer[bel_supp]
        self.bel_particle_filter = {k: 0 for k in bel_supp}
        self.energy = energy
        if self.cpomdp.belief_supp_cmdp.is_reload(self.bel_supp_state):
            self.energy = self.capacity
        self.exploration = exploration
        self.history = history
        self.action_shield = action_shield
        self.max_function = max_function
        self.belief = belief
        self.logger = logger

        for action in filter_safe_actions(
            self.action_shield, self.energy, self.bel_supp_state
        ):
            action_node = POMCPActionNode(cpomdp, self, action, self.logger)
            self.children.append(action_node)

    def simulate_action(self, sampled_state: int) -> Tuple[POMCPHistoryNode, int]:
        """Method for simulating finding best action according to UCT formula, or trying any unused action.
        For action nodes with equal highest UCT evaluation, selects randomly.

        Parameters
        ----------
        sampled_state : int
            State which was sampled and is used when sampling new observations and states in ActionNode-s.
        Returns
        -------
        Tuple[POMCPHistoryNode, int]
            A pair of new history node and particle (newly sampled state from next sampled history node's belief
             support).
        """

        unvisited_children = [
            action_node for action_node in self.children if action_node.visits == 0
        ]

        self.logger.debug(
            f"{len(self.children)} CHILDREN, OF THEM {len(unvisited_children)} ARE UNVISITED, ENERGY LEVEL: {self.energy}"
        )

        if len(unvisited_children) != 0:
            return random.sample(unvisited_children, 1)[0].sample_hist_node(
                sampled_state
            )

        uct_values = self.calculate_uct()

        self.logger.debug(f"BEST UCT: {max(uct_values)}, ALL UCT: {uct_values}")

        best_action_indices = [
            uct_values.index(i) for i in uct_values if i == max(uct_values)
        ]  # minimal depth, each step gives negative payoff
        return self.children[random.sample(best_action_indices, 1)[0]].sample_hist_node(
            sampled_state
        )

    def calculate_uct(self) -> List[float]:
        """Method for calculating UCT values for child action nodes.

        Returns
        -------
        List[float]
            Evaluations of child action nodes in order.
        """
        children_vals = [child.avg_val for child in self.children]
        children_visits = [child.visits for child in self.children]

        abs_max_val = max(map(abs, children_vals))
        divisor = abs_max_val if abs_max_val != 0 else 1

        normalized_vals = [
            float(val) / divisor for val in children_vals
        ]

        exploration_bonus = [
            2 * self.exploration * math.sqrt(math.log(self.visits) / children_visits[i])
            for i in range(len(children_visits))
        ]

        self.logger.log(7, f"NORMALIZED VALUES: {normalized_vals}")
        self.logger.log(7, f"EXPLORATION BONUSES: {exploration_bonus}")

        return [
            normalized_vals[i] + exploration_bonus[i]
            for i in range(len(children_visits))
        ]


class OnlineStrategy:
    """Online strategy interface class.

    Supported operations: update observation, get best action, reset the strategy.

    Attributes
    ----------
    tree : POMCPTree
        Tree where best actions are calculated using modified POMCP algorithm
    capacity : int
        Maximum energy of environment
    best_action : ActionData
        Current computed best action to play.
    solver : ConsPOMDPBasicES
        Solver for POMDP buchi safe actions.
    action_picked : bool
        Parameter for checking if correct order of strategy actions is taken
    """

    tree: POMCPTree
    capacity: int
    best_action: ActionData
    solver: ConsPOMDPBasicES
    action_picked: bool
    rollout_function: Callable[[int, int, int, int, int, bool], float]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        capacity: int,
        init_energy: int,
        init_obs: int,
        init_bel_supp: Tuple[int, ...],
        targets: List[int],
        exploration: float,
        rollout_function: Callable[[int, int, int, int, int, bool], float],
        rollout_horizon: int = 100,
        random_seed: int = 42,
        recompute: bool = False,  # In the case that belief and guess constructions are not computed, set to True
        solver: Optional[ConsPOMDPBasicES] = None,
        logger=None,
        softmax_on: bool = False
    ):
        if logger is None:
            logger = logging.getLogger(f"{random_seed}")

        if solver is None:
            self.solver = ConsPOMDPBasicES(
                cpomdp, list(init_bel_supp), capacity, targets, recompute
            )
            self.solver.compute_buchi()

        else:
            self.solver = solver

        action_shield = self.solver.get_buchi_safe_actions_bscmdp()

        self.action_picked = False

        self.tree = POMCPTree(
            cpomdp,
            targets,
            init_obs,
            init_bel_supp,
            capacity,
            init_energy,
            action_shield,
            exploration,
            random_seed,
            rollout_function,
            rollout_horizon,
            logger=logger,
            softmax_on=softmax_on
        )

    def update_obs(self, outcome: int) -> None:
        """Method signalizing the tree the new observation outcome

        Parameters
        ----------
        outcome : int
            Given observation outcome
        """
        if not self.action_picked:
            raise AttributeError(
                f"Can't update observation if you haven't found best next action yet."
            )
        self.tree.use_outcome(self.best_action, outcome)
        self.action_picked = False

    def next_action(self, iterations_count: int = 1000) -> ActionData:
        """Method for getting the next action.

        Parameters
        ----------
        iterations_count : int
            Max iterations for the POMCP simulation

        Returns
        -------
        ActionData
            Action picked by POMCP simulation.
        """
        if self.action_picked:
            raise AttributeError(
                f"Can't pick action if you haven't updated observation from previously picked action."
            )
        self.best_action = self.tree.best_action(iterations_count)
        self.action_picked = True
        return self.best_action

    def reset(
        self,
        init_energy: int,
        init_obs: int,
        init_bel_supp: Tuple[int, ...],
        exploration: float,
        init_belief: Dict[int, float],
        random_seed: int = 42,
    ) -> None:
        """Method for resetting the strategy with new initial conditions.

        Parameters
        ----------
        init_energy : int
            New initial energy.
        init_obs : int
            New initial observation.
        init_bel_supp : int
            New initial belief support.
        init_belief : Dict[int, float]
            New initial belief/particle filter result.
        exploration : float
            New exploration constant
        random_seed : int
            Random seed, defaults to 42.
        """
        self.tree.tree_reset(
            init_energy, init_obs, init_bel_supp, init_belief, exploration, random_seed
        )
