from typing import List

from fipomdp import ConsPOMDP


class TigerEnvironment:

    cpomdp: ConsPOMDP
    targets: List[int]
    capacity: int

    def __init__(self, cap: int):
        cpomdp = ConsPOMDP()

        cpomdp.new_state(False, "tiger_left")
        cpomdp.new_state(False, "tiger_right")

        cpomdp.new_state(True, "reload_tiger_left")
        cpomdp.new_state(True, "reload_tiger_right")

        cpomdp.new_state(False, "tiger")
        cpomdp.new_state(False, "reward")

        cpomdp.add_action(0, {0: 1}, "listen", 1)
        cpomdp.add_action(1, {1: 1}, "listen", 1)

        cpomdp.add_action(0, {2: 1}, "reload_action", 1)
        cpomdp.add_action(1, {3: 1}, "reload_action", 1)
        cpomdp.add_action(2, {0: 0.8, 1: 0.2}, "get_back", 0)
        cpomdp.add_action(3, {0: 0.2, 1: 0.8}, "get_back", 0)

        cpomdp.add_action(0, {4: 1}, "open_left", 0)
        cpomdp.add_action(0, {5: 1}, "open_right", 0)
        cpomdp.add_action(1, {4: 1}, "open_right", 0)
        cpomdp.add_action(1, {5: 1}, "open_left", 0)

        observation_probabilities = {(0, 0): 0.85, (0, 1): 0.15, (1, 0): 0.15, (1, 1): 0.85, (2, 2): 1, (3, 2): 1, (4, 3): 1, (5, 4): 1}

        cpomdp.set_observations(5, observation_probabilities, ["hear_tiger_left", "hear_tiger_right", "reload", "tiger", "reward"])

        self.cpomdp = cpomdp
        self.capacity = cap
        self.targets = [5]

    def get_cpomdp(self):
        return self.cpomdp, self.targets
