from __future__ import annotations

import math
import random
from functools import reduce
from typing import List, Tuple, Dict

import numpy

from fimdp.core import ActionData
from fipomdp import ConsPOMDP


class POMCPTree:
    root: POMCPHistoryNode
    cpomdp: ConsPOMDP
    iterations: int
    max_iterations: int
    current_node: POMCPHistoryNode
    action_shield: List[Tuple[int, ActionData]]
    exploration: float
    seed: int

    def __init__(self,
                 cpomdp: ConsPOMDP,
                 root_obs: int,
                 root_bel_supp: Tuple[int, ...],
                 action_shield: List[Tuple[int, ActionData]],
                 max_iterations: int,
                 exploration: float,
                 random_seed: int
        ):

        self.cpomdp = cpomdp
        self.iterations = 0
        self.max_iterations = max_iterations
        self.action_shield = action_shield
        self.exploration = exploration
        self.seed = random_seed

        self.root = POMCPHistoryNode(root_obs, root_bel_supp)
        self.current_node = self.root

    def history_eval(self, history_node: POMCPHistoryNode) -> float:
        return round(
            sum(map(self.state_eval, history_node.bel_supp)) / len(history_node.bel_supp),
        )

    def state_eval(self, state: int) -> float:
        random.seed(self.seed)
        return random.random()

    def iteration(self) -> None:
        pass

    def update(self, history, result) -> None:
        pass


class POMCPActionNode:
    action: ActionData
    visits: int
    val: float
    children: List[POMCPHistoryNode]

    def __init__(self, action: ActionData):
        self.action = action


class POMCPHistoryNode:
    children: List[POMCPActionNode]
    visits: int
    obs: int
    bel_supp: Tuple[int, ...]
    bel_particle_filter: Dict[int, int]
    energy: int
    history: List[Tuple[POMCPHistoryNode, ActionData]]
    val: float
    seed: int

    def __init__(self, obs: int, bel_supp: Tuple[int, ...], energy: int, history: List[Tuple[POMCPHistoryNode, ActionData]], seed: int) -> None:
        self.children = []
        self.visits = 0
        self.obs = obs
        self.bel_supp = bel_supp
        self.bel_particle_filter = {k: 0 for k in bel_supp}
        self.energy = energy
        self.history = history
        self.val = 0
        self.seed = seed

    def add_child(self, obs, bel_supp) -> None:
        child = POMCPActionNode(obs, bel_supp) # TODO!!!
        self.children.append(child)

    def sample(self, distribution: Dict[int, float]):
        keys = list(distribution.keys())
        values = list(distribution.values())
        random.seed(self.seed)
        return random.choices(population=keys, weights=values)

    def safe_actions(self, action_shield: List[Tuple[int, ActionData]]) -> List[ActionData]:
        

    def calculate_uct(self, uct_constant: float) -> List[float]:
        children_vals = [child.val for child in self.children]
        children_visits = [child.visits for child in self.children]
        normalized_vals = [float(val)/max(children_vals) for val in children_vals]

        return [normalized_vals[i] +
                2*uct_constant*math.sqrt(math.log(self.visits)/children_visits[i])
                for i in range(len(children_visits))
        ]

