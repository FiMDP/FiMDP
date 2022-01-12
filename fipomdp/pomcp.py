"""Module defining an Online Strategy using POMCP algorithm modified with shielding.

Classes used for POMCP:
 * POMCPTree - represents the tree with root, parameters needed to reset it,
                and methods for monte carlo iterations, rollouts, node updates, and picking the best action.
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
from typing import List, Tuple, Dict, Optional

from fimdp.core import ActionData
from fimdp.distribution import uniform
from fipomdp import ConsPOMDP
from fipomdp.energy_solvers import ConsPOMDPBasicES

import logging


class POMCPTree:
    """POMCP tree representation, with shielded actions.

    This tree representation uses only the root of the tree, rest of the tree is accessible through nodes themselves
    """

    root: POMCPHistoryNode
    cpomdp: ConsPOMDP
    targets: List[int]
    iterations: int
    capacity: int
    action_shield: List[Tuple[int, ActionData]]
    exploration: float
    rollout_horizon: int
    random_seed: int

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        targets: List[int],
        root_obs: int,
        root_bel_supp: Tuple[int, ...],
        capacity: int,
        energy: int,
        action_shield: List[Tuple[int, ActionData]],
        exploration: float,
        random_seed: int,
        rollout_horizon: int = 100,
        root_belief: Optional[Dict[int, float]] = None,
    ):

        logging.info(
            f"Constructing tree, parameters: \n"
            f"targets: {targets},\n"
            f"root observation: {root_obs},\n"
            f"root belief support: {root_bel_supp},\n"
            f"capacity: {capacity},\n"
            f"energy: {energy},\n"
            f"exploration: {exploration},\n"
            f"random seed: {random_seed},\n"
            f"rollout horizon: {rollout_horizon},\n"
            f"root belief: {root_belief}"
        )

        self.cpomdp = cpomdp
        self.targets = targets
        self.iterations = 0
        self.capacity = capacity
        self.action_shield = action_shield
        self.exploration = exploration
        self.rollout_horizon = rollout_horizon

        if root_belief is None:
            root_belief = {
                k: v
                for k, v in uniform(self.cpomdp.get_obs_states(root_obs)).items()
                if k in root_bel_supp
            }

        self.root = POMCPHistoryNode(
            cpomdp,
            self.capacity,
            root_obs,
            root_bel_supp,
            energy,
            exploration,
            [],
            action_shield,
            root_belief,
        )

        self.random_seed = random_seed
        random.seed(
            random_seed
        )  # Over the scope of the tree instance, and all the node instances in it

        logging.info(f"Tree created")

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
        while current_history_node.visits != 0:
            node, belief = current_history_node.simulate_action(tmp_sample)
            current_history_node = node
            belief_particles.append(belief)
            tmp_sample = belief

        self.iterations += 1

        print()
        print(f"ITERATION: {self.iterations}")
        print(f"BELIEF_PARTICLES: {belief_particles}")
        print()
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

        for (hist_node, act_node) in history:
            hist_node.visit(result)
            act_node.visit(result)

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

        logging.info(f"Launching tree run with {max_iterations} iterations")

        for i in range(max_iterations):

            sampled_state = sample_from_distr(self.root.belief)

            logging.info(
                f"Launching tree iteration and rollout with sampled state {sampled_state}."
            )

            iter_hist_node, iter_beliefs = self.iteration(sampled_state)

            print()

            if len(iter_beliefs) == 0:
                result = self.rollout(
                    iter_hist_node, sampled_state, self.rollout_horizon
                )
            else:
                result = self.rollout(
                    iter_hist_node, iter_beliefs[-1], self.rollout_horizon
                )

            self.update_tree(iter_hist_node, result, iter_beliefs)

            logging.info(
                f"Tree iteration finished, new history node has observation {iter_hist_node.obs} and belief support {iter_hist_node.bel_supp}"
            )
            logging.info(f"Rollout of this node has been evaluated as {result}")

        logging.info(f"Tree run finished")

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

        logging.info(
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
            belief,
        )

        self.iterations = 0
        self.random_seed = random_seed
        random.seed(random_seed)

        logging.info(f"Finished tree reset")

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

        logging.info(f"Picking best action from tree")

        self.tree_run(max_iterations)
        uct_values = self.root.calculate_uct()
        best_action_indices = [
            uct_values.index(i) for i in uct_values if i == min(uct_values)
        ]

        action_node = self.root.children[random.sample(best_action_indices, 1)[0]]
        action = action_node.bel_supp_action

        logging.info(
            f"{action} action was evaluated highest with value of {action_node.val}"
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
        result = 0
        energy = history_node.energy
        bel_supp_state = history_node.bel_supp_state
        safe_actions = filter_safe_actions(self.action_shield, energy, bel_supp_state)
        src_state = state

        for i in range(horizon):
            if len(safe_actions) == 0:
                return 3 * horizon * (-1)
            bs_action = random.sample(safe_actions, 1)[0]
            state_action = matching_state_action(self.cpomdp, bs_action, src_state)
            energy -= state_action.cons
            result -= 1
            new_state = sample_from_distr(state_action.distr)

            if self.cpomdp.is_reload(new_state):
                energy = self.capacity

            if new_state in self.targets:
                target_found = True
                break

            src_state = new_state
            new_bel_supps = [
                self.cpomdp.belief_supp_cmdp.bel_supps[i] for i in bs_action.distr
            ]
            for tmp_bel_supp in new_bel_supps:
                if new_state in tmp_bel_supp:
                    bel_supp_state = self.cpomdp.belief_supp_cmdp.bel_supp_indexer[
                        tuple(tmp_bel_supp)
                    ]

            safe_actions = filter_safe_actions(
                self.action_shield, energy, bel_supp_state
            )

        return result * (1 if target_found else 2)  # TODO discuss weight

    def use_outcome(self, action: ActionData, outcome: int):
        """Method for using new observation from previously selected (best) action
         to reset the tree after one tree run.

        Parameters
        ----------
        action : ActionData
            Previously selected action
        outcome : int
            New observation recieved
        """

        logging.info(f"Updating the tree with observation {outcome}")

        new_history_node = None
        for action_node in self.root.children:
            if action_node.bel_supp_action == action:
                for history_node in action_node.children:
                    if history_node.obs == outcome:
                        new_history_node = history_node
                        break
                break

        if new_history_node is None:
            raise ValueError(
                f"Error, new history node not found according to observation."
            )

        self.tree_reset(
            new_history_node.energy,
            outcome,
            new_history_node.bel_supp,
            new_history_node.bel_particle_filter,
            self.exploration,
            self.random_seed,
        )

        logging.info(f"New sampled node to fit observation was created")


class POMCPNode:
    """Class for abstract functionality of both types of nodes in POMCPTree.
    Supports only visits.

    Attributes
    ---------
    visits : int
        Number of visits in this node.
    val : float
        Current value of this node.
    """

    cpomdp: ConsPOMDP
    visits: int
    val: float

    def __init__(self, cpomdp: ConsPOMDP):
        self.cpomdp = cpomdp
        self.visits = 0
        self.val = 0

    def visit(self, value: float) -> None:
        """Method for visiting this node and update its value average.

        Parameters
        ----------
        value : float
            New value for update.
        """
        self.val = (self.val * self.visits + value) / (self.visits + 1)
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
    ):

        super(POMCPActionNode, self).__init__(cpomdp)
        self.parent_node = parent_node
        self.bel_supp_action = bel_supp_action
        self.children = []

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

        print()
        print(f"ALL BELIEF SUPPS: {belief_supps}")
        print(
            f"BELIEF SUPP ACITON: {self.bel_supp_action}, SRC BELIEF: {self.cpomdp.belief_supp_cmdp.bel_supps[self.bel_supp_action.src]}"
        )

        timeout = 0
        belief_supp = ()

        while (
            belief_supp == () and timeout < 1000 and len(cpomdp_state_action_distr) > 0
        ):
            dest_state = sample_from_distr(cpomdp_state_action_distr)
            obs_distr = self.cpomdp.get_state_obs_probs(dest_state)

            print(f"OBS_DISTR: {obs_distr}")
            print(f"MATCHING STATE ACITON: {cpomdp_state_action}")

            while len(obs_distr) > 0 and belief_supp == ():
                dest_obs = sample_from_distr(obs_distr)
                dest_obs_states = self.cpomdp.get_obs_states(dest_obs)

                for b_s in belief_supps:
                    if dest_state in b_s and len(belief_supp) < len(b_s) == len(
                        [state for state in b_s if state in dest_obs_states]
                    ):
                        belief_supp = b_s

                obs_distr.pop(dest_obs)

            if dest_state not in belief_supp:
                belief_supp = ()
                cpomdp_state_action_distr.pop(dest_state)

        if belief_supp == ():
            print("FATAL ERROR coming up")
            print(
                f"SRC_STATE: {state}, DEST STATE: {dest_state}, OBS: {dest_obs}, DEST BELIEF_SUPP: {belief_supps}"
            )
            raise ValueError(
                f"Couldn't match observation, for belief_supps: {belief_supps} and state: {dest_state}"
            )

        print(f"PICKED BELIEF SUPP: {belief_supp}")

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
    action_shield: List[Tuple[int, ActionData]]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        capacity: int,
        obs: int,
        bel_supp: Tuple[int, ...],
        energy: int,
        exploration: float,
        history: List[Tuple[POMCPHistoryNode, POMCPActionNode]],
        action_shield: List[Tuple[int, ActionData]],
        belief: Optional[Dict[int, float]] = None,
    ) -> None:
        super(POMCPHistoryNode, self).__init__(cpomdp)
        if belief is None:
            belief = {}
        self.capacity = capacity
        self.children = []
        self.obs = obs
        self.bel_supp = bel_supp
        self.bel_supp_state = cpomdp.belief_supp_cmdp.bel_supp_indexer[bel_supp]
        self.bel_particle_filter = {k: 0 for k in bel_supp}
        self.energy = energy
        self.exploration = exploration
        self.history = history
        self.action_shield = action_shield
        self.belief = belief

        for action in filter_safe_actions(
            self.action_shield, self.energy, self.bel_supp_state
        ):
            action_node = POMCPActionNode(cpomdp, self, action)
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

        print(
            f"{len(self.children)} CHILDREN, OF THEM {len(unvisited_children)} ARE UNVISITED, ENERGY LEVEL: {self.energy}"
        )

        if len(unvisited_children) != 0:
            return random.sample(unvisited_children, 1)[0].sample_hist_node(
                sampled_state
            )

        uct_values = self.calculate_uct()
        print(f"BEST UCT: {min(uct_values)}, ALL UCT: {uct_values}")
        best_action_indices = [
            uct_values.index(i) for i in uct_values if i == min(uct_values)
        ]  # minimal depth
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
        children_vals = [child.val for child in self.children]
        children_visits = [child.visits for child in self.children]
        normalized_vals = [
            float(val) / max(map(abs, children_vals)) for val in children_vals
        ]

        exploration_bonus = [
            2 * self.exploration * math.sqrt(math.log(self.visits) / children_visits[i])
            for i in range(len(children_visits))
        ]

        print(f"NORMALIZED VALUES: {normalized_vals}")
        print(f"EXPLORATION BONUSES: {exploration_bonus}")

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

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        capacity: int,
        init_energy: int,
        init_obs: int,
        init_bel_supp: Tuple[int, ...],
        targets: List[int],
        exploration: float,
        rollout_horizon: int = 100,
        random_seed: int = 42,
        recompute: bool = False,  # In the case that belief and guess constructions are not computed, set to True
    ):

        self.solver = ConsPOMDPBasicES(
            cpomdp, list(init_bel_supp), capacity, targets, recompute
        )
        self.solver.compute_buchi()
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
            rollout_horizon,
            random_seed,
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
        self.action_picked = False
        self.tree.use_outcome(self.best_action, outcome)

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
