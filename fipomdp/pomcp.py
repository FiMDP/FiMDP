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
from typing import List, Tuple, Dict

from fimdp.core import ActionData
from fipomdp import ConsPOMDP
from fipomdp.energy_solvers import ConsPOMDPBasicES


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
        rollout_horizon: int = 20,
    ):

        self.cpomdp = cpomdp
        self.targets = targets
        self.iterations = 0
        self.capacity = capacity
        self.action_shield = action_shield
        self.exploration = exploration
        self.rollout_horizon = rollout_horizon

        self.root = POMCPHistoryNode(
            cpomdp, root_obs, root_bel_supp, energy, exploration, [], action_shield
        )

        random.seed(
            random_seed
        )  # Over the scope of the tree instance, and all the node instances in it

    def iteration(self) -> Tuple[POMCPHistoryNode, List[int]]:
        """Method for simulating one iteration of POMCP algorithm.

        Traverses the tree downwards and when it reaches leaf node, picks action one last time and returns the newly
        created history node, along with accumulated particles along the way.

        Returns
        -------
        Tuple[POMCPHistoryNode, List[int]]
            Pair of newest history node and particles to update the tree with.

        """
        current_history_node = self.root
        belief_particles = []
        while current_history_node.visits != 0:
            node, belief = current_history_node.simulate_action()
            current_history_node = node
            belief_particles.append(belief)
        return current_history_node, belief_particles

    def update_tree(
        self,
        history_node: POMCPHistoryNode,
        result: float,
        belief_particles: List[int],
        root_sample: int,
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
        root_sample : int
            Given sample of root node to update its belief.
        """
        history = history_node.history

        if len(history) != len(belief_particles):
            raise AttributeError(
                f"Incorrect parameters: history with length {len(history)} has different length than belief particles: {len(belief_particles)}."
            )

        self.root.bel_particle_filter[root_sample] += 1

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
        history_node.bel_particle_filter[belief_particles[-1]] += 1

    def tree_run(self, max_iterations: int) -> None:
        """Method for simulating one full tree run, with all iterations, rollouts and updates.

        Parameters
        ----------
        max_iterations: int
            Number of max iterations.
        """
        for i in range(max_iterations):
            iter_hist_node, iter_beliefs = self.iteration()
            history = iter_hist_node.history
            result = self.rollout(
                iter_hist_node, iter_beliefs[-1], self.rollout_horizon
            )
            self.update_tree(history, result)

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
        self.tree_run(max_iterations)
        uct_values = self.root.calculate_uct()
        best_action_indices = [
            uct_values.index(i) for i in uct_values if i == min(uct_values)
        ]
        return self.root.children[
            random.sample(best_action_indices, 1)[0]
        ].bel_supp_action

    def tree_reset(
        self,
        energy: int,
        obs: int,
        bel_supp: Tuple[int, ...],
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
        """
        self.root = POMCPHistoryNode(
            self.cpomdp, obs, bel_supp, energy, exploration, [], self.action_shield
        )

        self.iterations = 0
        random.seed(random_seed)

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
            bs_action = random.sample(safe_actions, 1)[0]
            state_action = matching_state_action(self.cpomdp, bs_action, src_state)
            energy -= state_action.cons
            result -= 1
            new_state = sample_from_distr(state_action.distr)

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
        dest_state = sample_from_distr(cpomdp_state_action.distr)
        bel_supp_dest_states = self.bel_supp_action.get_succs()
        obs_distr = self.cpomdp.get_state_obs_probs(dest_state)
        belief_supps = [
            self.cpomdp.belief_supp_cmdp.bel_supps[bel_supp_state]
            for bel_supp_state in bel_supp_dest_states
        ]
        belief_supp = ()
        possible_obs_distr = {}
        for b_s in belief_supps:
            if dest_state in b_s:
                belief_supp = tuple(b_s)
                possible_obss = self.cpomdp.get_states_obss_possible(b_s)
                possible_obs_distr = {k: v for k, v in obs_distr if k in possible_obss}

        sample_obs = sample_from_distr(possible_obs_distr)

        for hist_node in self.children:
            if hist_node.bel_supp == belief_supp and hist_node.obs == sample_obs:
                return hist_node, dest_state

        new_hist = copy(self.parent_node.history)
        new_hist.append((self.parent_node, self))
        new_child = POMCPHistoryNode(
            self.cpomdp,
            sample_obs,
            belief_supp,
            self.parent_node.energy - self.bel_supp_action.cons,
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
    children: List[POMCPActionNode]
    obs: int
    bel_supp: Tuple[int, ...]
    bel_particle_filter: Dict[int, int]
    energy: int
    exploration: float
    history: List[Tuple[POMCPHistoryNode, POMCPActionNode]]
    action_shield: List[Tuple[int, ActionData]]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        obs: int,
        bel_supp: Tuple[int, ...],
        energy: int,
        exploration: float,
        history: List[Tuple[POMCPHistoryNode, POMCPActionNode]],
        action_shield: List[Tuple[int, ActionData]],
    ) -> None:
        super(POMCPHistoryNode, self).__init__(cpomdp)
        self.children = []
        self.obs = obs
        self.bel_supp = bel_supp
        self.bel_supp_state = cpomdp.belief_supp_cmdp.bel_supp_indexer[bel_supp]
        self.bel_particle_filter = {k: 0 for k in bel_supp}
        self.energy = energy
        self.exploration = exploration
        self.history = history
        self.action_shield = action_shield

        for action in filter_safe_actions(
            self.action_shield, self.energy, self.bel_supp_state
        ):
            action_node = POMCPActionNode(cpomdp, self, action)
            self.children.append(action_node)

    def simulate_action(self) -> Tuple[POMCPHistoryNode, int]:
        unvisited_children = [
            action_node for action_node in self.children if action_node.visits == 0
        ]
        if len(unvisited_children) != 0:
            return random.sample(unvisited_children, 1)[0].sample_hist_node()
        uct_values = self.calculate_uct()
        best_action_indices = [
            uct_values.index(i) for i in uct_values if i == min(uct_values)
        ]  # minimal depth
        return self.children[
            random.sample(best_action_indices, 1)[0]
        ].sample_hist_node()

    def calculate_uct(self) -> List[float]:
        children_vals = [child.val for child in self.children]
        children_visits = [child.visits for child in self.children]
        normalized_vals = [
            float(val) / max(map(abs, children_vals)) for val in children_vals
        ]

        return [
            normalized_vals[i]
            + 2
            * self.exploration
            * math.sqrt(math.log(self.visits) / children_visits[i])
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
    """

    tree: POMCPTree
    capacity: int

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        capacity: int,
        init_energy: int,
        init_obs: int,
        init_bel_supp: Tuple[int, ...],
        targets: List[int],
        exploration: float,
        random_seed: int = 42,
    ):

        solver = ConsPOMDPBasicES(cpomdp, list(init_bel_supp), capacity, targets)
        solver.compute_buchi()
        action_shield = solver.get_buchi_safe_actions_bscmdp()

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
        )

    def update_obs(self, outcome: int):
        pass  # TODO

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
        return self.tree.best_action(iterations_count)

    def reset(
        self,
        init_energy: int,
        init_obs: int,
        init_bel_supp: Tuple[int, ...],
        exploration: float,
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
        exploration : float
            New exploration constant
        random_seed : int
            Random seed, defaults to 42.
        """
        self.tree.tree_reset(
            init_energy, init_obs, init_bel_supp, exploration, random_seed
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
        if min_energy < energy and action.src == bel_supp_state
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
