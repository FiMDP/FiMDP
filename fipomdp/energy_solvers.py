"""Module with non goal-leaning, energy-aware, qualitative solver for Consumption POMDPs

Supported objectives:
 * safe
 * positive reachability(target)
 * büchi(target)
"""
import logging
from typing import List, Dict, Tuple

from fimdp.core import ActionData
from fimdp.energy_solvers import BasicES
from fimdp.objectives import SAFE, POS_REACH, BUCHI
from fipomdp import ConsPOMDP


class ConsPOMDPBasicES:

    cpomdp: ConsPOMDP
    bel_supp_ES: BasicES
    guessing_ES: BasicES
    cap: int

    bs_min_levels: Dict[int, List[int]]
    guess_min_levels: Dict[int, List[int]]

    def __init__(
        self,
        cpomdp: ConsPOMDP,
        belief_supp: List[int],
        cap: int,
        cpomdp_targets: List[int],
        recompute: bool = False,
    ):
        logging.info(f"Creating solver")

        self.cpomdp = cpomdp
        self.cap = cap

        if recompute:
            cpomdp.compute_guessing_cmdp_initial_state(belief_supp)
        else:
            logging.info(
                f"Reusing precomputed belief support cmdp and guessing cmdp of cpomdp."
            )

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

        self.bs_min_levels = {}
        self.guess_min_levels = {}

        logging.info(f"Solver created")

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
        self.bs_min_levels[SAFE] = self.bel_supp_ES.min_levels[SAFE]
        self.guess_min_levels[SAFE] = self._guessing_min_safe_levels(
            self.bel_supp_ES.min_levels[SAFE]
        )

    def compute_posreach(self) -> None:

        logging.info("Solving POS_REACH values")

        self.guessing_ES.compute(POS_REACH)
        self.guess_min_levels[POS_REACH] = self.guessing_ES.min_levels[POS_REACH]

        logging.info("POS_REACH values solved")

    def compute_buchi(self) -> None:

        logging.info("Solving BUCHI values")

        original_reloads = list(self.cpomdp.guessing_cmdp.reloads)
        fixpoint = False
        while not fixpoint:
            fixpoint = True
            self.compute_posreach()
            for i in range(self.cpomdp.guessing_cmdp.num_states):
                if (
                    self.cpomdp.guessing_cmdp.is_reload(i)
                    and self.cpomdp.guessing_cmdp.belief_supp_guess_pairs[i][1]
                    is not None
                    and self.guess_min_levels[POS_REACH][i] > self.cap
                ):
                    fixpoint = False
                    unusable_reloads = self.cpomdp.guessing_cmdp.belief_supp_states(
                        self.cpomdp.guessing_cmdp.belief_supp_guess_pairs[i][0]
                    )
                    for state in unusable_reloads:
                        self.cpomdp.guessing_cmdp.set_reload(state, False)

        self.guess_min_levels[BUCHI] = list(self.guess_min_levels[POS_REACH])
        bs_min_levels = [-1 for _ in range(self.cpomdp.belief_supp_cmdp.num_states)]

        for i in range(self.cpomdp.guessing_cmdp.num_states):
            belief_support, guess = self.cpomdp.guessing_cmdp.belief_supp_guess_pairs[i]
            bs_index = self.cpomdp.belief_supp_cmdp.bel_supp_indexer[
                tuple(belief_support)
            ]
            if (
                bs_min_levels[bs_index] < self.guess_min_levels[BUCHI][i]
                and guess is not None
            ):
                bs_min_levels[bs_index] = self.guess_min_levels[BUCHI][i]
            logging.log(5, f"BELIEF SUPPORT MIN LEVELS: {bs_min_levels}")

        self.bs_min_levels[BUCHI] = bs_min_levels
        self.cpomdp.guessing_cmdp.reloads = original_reloads
        self.compute_posreach()

        logging.info("BUCHI values solved")

    def get_buchi_safe_actions_bscmdp(self) -> Dict[int, Dict[ActionData, int]]:

        logging.info("Creating action shield")

        bsafe_actions = dict()
        for i in range(self.cpomdp.belief_supp_cmdp.num_states):
            bsafe_bel_supp_state_actions = dict()
            for action in self.cpomdp.belief_supp_cmdp.actions_for_state(i):
                safe_level = action.cons
                for succ in action.get_succs():
                    if not self.cpomdp.belief_supp_cmdp.reloads[succ]:
                        safe_level = max(
                            safe_level, action.cons + self.bs_min_levels[BUCHI][succ]
                        )
                    # safe_level = -1000000  # SHIELD OFF
                bsafe_bel_supp_state_actions[action] = safe_level
            bsafe_actions[i] = bsafe_bel_supp_state_actions

        logging.info(f"Action shield created.")

        return bsafe_actions
