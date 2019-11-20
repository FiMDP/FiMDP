from reachability import Reachability
from math import inf
from energy_levels import largest_fixpoint

class Buchi(Reachability):
    """Compute energy needed to safely satisy Büchi objective
    for a target set `targets`

    `targets` : `set of ints` target states
    """

    def __init__(self, mdp, targets, cap = inf):
        Reachability.__init__(self, mdp, targets, cap)

        self.buchi_values = None
        self.buchi_safe   = [inf] * self.states

        self.get_safe()

    def get_Buchi(self, recompute=False):
        """Return (and compute) minimal levels for Buchi
        objective with `self.targets` and `self.capacity`.

        When called for the first time, compute the values.
        Recomputes the values if requested by `recompute`.

        A Bellman-style equation largest fixpoint solver.

        On the high level, repeats following until fixpoint:
          1. compute PosReach_M
          2. NonReach = {r is reload and PosReach_M[r] = ∞}
          3. M = M \ NonReach

        The PosReach_M is computed as:
          1.1. Safe_M (largest_fixpoint)
          1.2. PosReach_M[t] = Safe_M[t] for targets
          1.3. fixpoint that navigates to T

        This guarantees that we can always keep in states that
        have positive probability of reaching T and that we can
        always eventualy reach energy sufficient to navigate
        towards T.

        In contrast to almostSureReachability here we do not set
        the buchi_safe values of targets to safe_values after 
        each iteration. This si because after reaching a target,
        we still need to reach target again. So the steps 1.1 and
        1.2 slightly differ. Otherwise, the computation is the same.

        The first iteration (the first fixpoint achieved) is equal
        to positive reachability.
        """
        if not recompute and self.buchi_values is not None:
            return self.buchi_values

        # removed stores reloads that had been removed from the MDP
        removed = set()

        done = False
        while not done:
            ### 1.1. Compute Safe(M\removed) and store it in buchi_safe
            self.sufficient_levels(removed, self.buchi_safe)

            ### 1.2. Initialization of PosReach_M
            #  * buchi_safe for target states
            #  * inf otherwise
            self.buchi_values = [inf] * self.states
            for t in self.targets:
                self.buchi_values[t] = self.buchi_safe[t]

            ### 1.3. Computation of PosReach on sub-MDP (with removed reloads)
            ## how much do I need to survive via this state after reloads removal
            # Use Safe_m (stored in buchi_safe) as value needed for survival
            rem_survival_val = lambda s: self.buchi_safe[s]
            # Navigate towards T and survive with Safe_m
            rem_action_value = lambda a, v: self.action_value_T(a, v, rem_survival_val)

            ## Avoid unnecessary computations
            is_removed = lambda x: x in removed # always ∞
            is_target  = lambda x: x in self.targets # always Safe_M
            skip_cond  = lambda x: is_removed(x) or is_target(x)

            ## Finish the fixpoint
            largest_fixpoint(self.mdp, self.buchi_values,
                             rem_action_value,
                             value_adj=self.reload_capper,
                             skip_state=skip_cond)

            ### 2. & 3. Detect bad reloads and remove them
            done = True
            # Iterate over reloads and remove unusable ones (∞)
            for s in range(self.states):
                if self.is_reload(s) and self.buchi_values[s] == inf:
                    if s not in removed:
                        removed.add(s)
                        done = False

        return self.buchi_values
