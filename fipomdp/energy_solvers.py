"""Module with non goal-leaning, energy-aware, qualitative solver for Consumption POMDPs

Supported objectives:
 * safe
 * positive reachability(target)
 * büchi(target)
"""

from typing import List, Dict, Optional

from fimdp.core import Strategy, ConsMDP, CounterSelector
from fimdp.energy_solvers import BasicES
from fimdp.objectives import SAFE, POS_REACH, BUCHI
from fipomdp import ConsPOMDP


class ConsPOMDPBasicES:

    cpomdp: ConsPOMDP
    bel_supp_ES: BasicES
    guessing_ES: BasicES
    cap: int

    min_levels: Dict[int, List[int]]
    helper_levels: Dict[int, List[int]]

    guess_selector: CounterSelector

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        belief_supp: List[int],
        cap: int,
        cpomdp_targets: List[int],
    ):
        self.cpomdp = cpomdp
        self.cap = cap
        cpomdp.compute_guessing_cmdp_initial_state(belief_supp)

        self.bel_supp_ES = BasicES(self.cpomdp.belief_supp_cmdp, cap, [])

        guessing_cmdp_targets = []
        for i in range(
            self.cpomdp.guessing_cmdp.num_states
        ):  # convert pomdp targets into guess targets
            if (
                self.cpomdp.guessing_cmdp.belief_supp_guess_pairs[i][1]
                in cpomdp_targets
            ):
                guessing_cmdp_targets.append(i)
        self.guessing_ES = BasicES(
            self.cpomdp.guessing_cmdp, cap, guessing_cmdp_targets
        )

        self.min_levels = {}
        self.helper_levels = {}

    def _guessing_min_safe_levels(self, bel_supp_min_levels: List[int]) -> List[int]:
        min_levels = []
        for i in range(self.cpomdp.guessing_cmdp.num_states):
            min_levels.append(
                bel_supp_min_levels[
                    self.cpomdp.belief_supp_cmdp.bel_supp_indexer[
                        tuple(self.cpomdp.guessing_cmdp.belief_supp_guess_pairs[i][0])
                    ]
                ]
            )
        return min_levels

    def compute_safe(self) -> None:
        self.bel_supp_ES.compute(SAFE)
        self.min_levels[SAFE] = self._guessing_min_safe_levels(
            self.bel_supp_ES.min_levels[SAFE]
        )

    def compute_posreach(self) -> None:
        self.guessing_ES.compute(POS_REACH)
        self.min_levels[POS_REACH] = self.guessing_ES.min_levels[POS_REACH]

    def compute_buchi(self) -> None:
        original_reloads = list(self.cpomdp.guessing_cmdp.reloads)
        fixpoint = False
        while not fixpoint:
            fixpoint = True
            self.compute_posreach()
            for i in range(self.cpomdp.guessing_cmdp.num_states):
                if (
                    self.cpomdp.guessing_cmdp.is_reload(i)
                    and self.min_levels[POS_REACH][i] > self.cap
                ):
                    fixpoint = False
                    unusable_reloads = self.cpomdp.guessing_cmdp.belief_supp_states(
                        self.cpomdp.guessing_cmdp.belief_supp_guess_pairs[i][0]
                    )
                    for state in unusable_reloads:
                        self.cpomdp.guessing_cmdp.set_reload(state, False)
        self.min_levels[BUCHI] = list(self.min_levels[POS_REACH])
        self.cpomdp.guessing_cmdp.reloads = original_reloads
        self.compute_posreach()
        self.guess_selector = self.guessing_ES.get_selector(BUCHI)


class POMDPStrategy(Strategy):
    def _next_action(self):
        pass

    cap: int

    def __init__(
        self, mdp: ConsMDP, cap: int, init_state: Optional[int] = None, *args, **kwargs
    ):
        super(POMDPStrategy, self).__init__(mdp, init_state, args, kwargs)
        self.cap = cap
