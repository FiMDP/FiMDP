from typing import List

from fimdp import ConsMDP
from fipomdp.core import ConsPOMDP


class BeliefSuppConsMDP(ConsMDP):
    original_cpomdp: ConsPOMDP
    belief_supports: List[List[int]]
    original_observations: List[int]

    def __init__(self, original_cpomdp: ConsPOMDP):
        super(BeliefSuppConsMDP, self).__init__()
        self.original_cpomdp = original_cpomdp
        original_observations = []
        belief_supports = []

    def new_state(self, original_obs: int, reload: bool = False, name: str = None, belief_support: List[int] = []):
        super(BeliefSuppConsMDP, self).new_state(reload, name)
        self.original_observations.append(original_obs)
        self.belief_supports.append(belief_support)

    def new_states(self, original_obs: int, count, names=None, belief_supports=None):
        super(BeliefSuppConsMDP, self).new_states(count, names)
        self.belief_supports.extend(belief_supports)
        self.original_observations.extend([original_obs for _ in range(count)])
