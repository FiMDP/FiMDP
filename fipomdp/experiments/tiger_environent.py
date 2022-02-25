from typing import List

from fipomdp import ConsPOMDP


class TigerEnvironment:

    cpomdp: ConsPOMDP
    targets: List[int]
    capacity: int

    def __init__(self, cap: int):
        cpomdp = ConsPOMDP()

        cpomdp.new_state(False, "init_left")
        cpomdp.new_state(False, "init_right")

        cpomdp.new_state(False, "tiger_left")
        cpomdp.new_state(False, "tiger_right")

        cpomdp.new_state(True, "reload_tiger_left")
        cpomdp.new_state(True, "reload_tiger_right")

        cpomdp.new_state(True, "tiger")
        cpomdp.new_state(True, "reward")

        cpomdp.add_action(0, {2: 1}, "listen", 1)
        cpomdp.add_action(1, {3: 1}, "listen", 1)

        cpomdp.add_action(2, {2: 1}, "listen", 1)
        cpomdp.add_action(3, {3: 1}, "listen", 1)

        cpomdp.add_action(2, {4: 1}, "reload_action", 1)
        cpomdp.add_action(3, {5: 1}, "reload_action", 1)
        cpomdp.add_action(4, {2: 0.8, 3: 0.2}, "get_back", 0)
        cpomdp.add_action(5, {2: 0.2, 3: 0.8}, "get_back", 0)

        cpomdp.add_action(2, {6: 1}, "open_left", 0)
        cpomdp.add_action(2, {7: 1}, "open_right", 0)
        cpomdp.add_action(3, {6: 1}, "open_right", 0)
        cpomdp.add_action(3, {7: 1}, "open_left", 0)

        cpomdp.add_action(6, {6: 1}, "sink", 0)
        cpomdp.add_action(7, {7: 1}, "sink", 0)

        observation_probabilities = {(0, 0): 1, (1, 0): 1, (2, 1): 0.85, (2, 2): 0.15, (3, 1): 0.15, (3, 2): 0.85, (4, 3): 1, (5, 3): 1, (6, 4): 1, (7, 5): 1}

        cpomdp.set_observations(6, observation_probabilities, ["init", "hear_tiger_left", "hear_tiger_right", "reload", "tiger", "reward"])

        self.cpomdp = cpomdp
        self.capacity = cap
        self.targets = [6, 7]

    def get_cpomdp(self):
        return self.cpomdp, self.targets
