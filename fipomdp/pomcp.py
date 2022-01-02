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
    iterations: int
    capacity: int
    action_shield: List[Tuple[int, ActionData]]
    exploration: float

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        root_obs: int,
        root_bel_supp: Tuple[int, ...],
        capacity: int,
        energy: int,
        action_shield: List[Tuple[int, ActionData]],
        exploration: float,
        random_seed: int,
    ):

        self.cpomdp = cpomdp
        self.iterations = 0
        self.capacity = capacity
        self.action_shield = action_shield
        self.exploration = exploration

        self.root = POMCPHistoryNode(cpomdp, root_obs, root_bel_supp, energy, exploration, [], action_shield)

        random.seed(
            random_seed
        )  # Over the scope of the tree instance, and all the node instances in it

    def history_node_eval(self, history_node: POMCPHistoryNode) -> float:
        return len(history_node.history)  # depth of the node

    def iteration(self) -> POMCPHistoryNode:
        current_history_node = self.root
        while current_history_node.visits != 0:
            current_history_node.pick_action()
        return current_history_node

    def update_tree(self, history, result) -> None:
        for (hist_node, act_node) in history:
            hist_node.visit(result)
            act_node.visit(result)

    def tree_run(self, max_iterations: int) -> None:
        for i in range(max_iterations):
            iter_hist_node = self.iteration()
            history = iter_hist_node.history
            result = self.history_node_eval(iter_hist_node)
            self.update_tree(history, result)

    def best_action(self, max_iterations: int) -> ActionData:
        self.tree_run(max_iterations)
        uct_values = self.root.calculate_uct()
        best_action_indices = [uct_values.index(i) for i in uct_values if i == min(uct_values)]
        return self.root.children[random.sample(best_action_indices, 1)[0]].bel_supp_action

    def tree_reset(self, energy, obs, bel_supp, exploration, random_seed):
        self.root = POMCPHistoryNode(self.cpomdp, obs, bel_supp, energy, exploration, [], self.action_shield)

        self.iterations = 0
        random.seed(random_seed)


class POMCPNode:
    cpomdp: ConsPOMDP
    visits: int
    val: float

    def __init__(self, cpomdp: ConsPOMDP):
        self.cpomdp = cpomdp
        self.visits = 0
        self.val = 0

    def visit(self, value: float):
        self.val = (self.val * self.visits + value) / (self.visits+1)
        self.visits += 1


class POMCPActionNode(POMCPNode):
    parent_node: POMCPHistoryNode
    bel_supp_action: ActionData
    children: List[POMCPHistoryNode]

    def __init__(self,
                 cpomdp: ConsPOMDP,
                 parent_node: POMCPHistoryNode,
                 bel_supp_action: ActionData):

        super(POMCPActionNode, self).__init__(cpomdp)
        self.parent_node = parent_node
        self.bel_supp_action = bel_supp_action
        self.children = []

    def sample_hist_node(self) -> Tuple[POMCPHistoryNode, int]:
        dest_state = sample(self.cpomdp_action.distr)
        bel_supp_dest_states = self.bel_supp_action.get_succs()
        obs_distr = self.cpomdp.get_state_obs_probs(dest_state)
        belief_supps = [self.cpomdp.belief_supp_cmdp.bel_supps[bel_supp_state]
                        for bel_supp_state in bel_supp_dest_states]
        belief_supp = ()
        possible_obs_distr = {}
        for b_s in belief_supps:
            if dest_state in b_s:
                belief_supp = tuple(b_s)
                possible_obss = self.cpomdp.get_states_obss_possible(b_s)
                possible_obs_distr = {k: v for k, v in obs_distr if k in possible_obss}

        sample_obs = sample(possible_obs_distr)

        for hist_node in self.children:
            if hist_node.bel_supp == belief_supp and hist_node.obs == sample_obs:
                return hist_node, dest_state

        new_hist = copy(self.parent_node.history)
        new_hist.append((self.parent_node, self))
        new_child = POMCPHistoryNode(
            self.cpomdp,
            sample_obs,
            belief_supp,
            self.parent_node.energy-self.bel_supp_action.cons,
            self.parent_node.exploration,
            new_hist,
            self.parent_node.action_shield)
        self.children.append(new_child)

        return new_child, dest_state


def sample(distribution: Dict[int, float]) -> int:
    keys = list(distribution.keys())
    values = list(distribution.values())
    return random.choices(population=keys, weights=values, k=1)[0]


class POMCPHistoryNode(POMCPNode):
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
        action_shield: List[Tuple[int, ActionData]]
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

        for action in self._safe_actions():
            action_node = POMCPActionNode(cpomdp, self, action)
            self.children.append(action_node)

    def pick_action(self) -> POMCPHistoryNode:
        unvisited_children = [action_node for action_node in self.children if action_node.visits == 0]
        if len(unvisited_children) != 0:
            return random.sample(unvisited_children, 1)[0].sample_hist_node()
        uct_values = self.calculate_uct()
        best_action_indices = [uct_values.index(i) for i in uct_values if i == min(uct_values)]  # minimal depth
        return self.children[random.sample(best_action_indices, 1)[0]].sample_hist_node()

    def calculate_uct(self) -> List[float]:
        children_vals = [child.val for child in self.children]
        children_visits = [child.visits for child in self.children]
        normalized_vals = [float(val) / max(map(abs, children_vals)) for val in children_vals]

        return [
            normalized_vals[i] + 2
            * self.exploration
            * math.sqrt(math.log(self.visits) / children_visits[i])
            for i in range(len(children_visits))
        ]

    def _safe_actions(
        self
    ) -> List[ActionData]:
        return [
            action
            for min_energy, action in self.action_shield
            if min_energy < self.energy and action.src == self.bel_supp_state
        ]


class OnlineStrategy:

    tree: POMCPTree
    capacity: int

    def __init__(self, cpomdp: ConsPOMDP, capacity: int, init_energy: int, init_obs: int, init_bel_supp: Tuple[int, ...], targets: List[int], exploration: float, random_seed: int = 42):

        solver = ConsPOMDPBasicES(cpomdp, list(init_bel_supp), capacity, targets)
        solver.compute_buchi()
        action_shield = solver.get_buchi_safe_actions_bscmdp()

        self.tree = POMCPTree(cpomdp, init_obs, init_bel_supp, capacity, init_energy, action_shield, exploration, random_seed)

    def update_obs(self, outcome: int):
        pass  # TODO

    def next_action(self, iterations_count: int = 1000) -> ActionData:
        return self.tree.best_action(iterations_count)

    def reset(self, init_energy: int, init_obs: int, init_bel_supp: Tuple[int, ...], exploration: float, random_seed: int = 42):
        self.tree.tree_reset(init_energy, init_obs, init_bel_supp, exploration, random_seed)

