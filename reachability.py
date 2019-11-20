from energy_levels import EnergyLevels, largest_fixpoint
from math import inf
class Reachability(EnergyLevels):
    """Compute energy needed to safely reach target set T with
    probability > 0.
    
    Expressed as largest fixpoint of a Bellman-style equation.
    The value of the action chooses a successor that we rely on
    for reaching the target and that has minimal value. The value
    of this successor is the energy needed to safely reach T via this
    successor + the safe energy level from the possibly-reached target
    state, or the energy needed to survive in some other successor
    under the action, whatever is higher.
    
    `targets` : `set of ints` target states
    """

    def __init__(self, mdp, targets, cap = inf):
        EnergyLevels.__init__(self, mdp, cap)

        self.targets = targets
        self.pos_reach_values = None
        self.alsure_values = None
        self.reach_safe_val = [inf] * self.states

    def reload_capper(self, s, v):
        """Reloads with value < capacity should be 0,
        anything above capacity should be ∞
        """
        # +1 handles cases when self.cap is ∞
        if v >= self.cap+1:
            return inf
        if self.is_reload(s):
            return 0
        return v

    def get_positiveReachability(self, recompute=False):
        """Return (and compute) minimal levels for positive
        reachability of `self.targets` and `self.capacity`.

        When called for the first time, compute the values.
        Recomputes the values if requested by `recompute`.

        A Bellman-style equation largest fixpoint solver.

        We start with ∞ for every state and propagate the safe energy
        needed to reach T from the target states further.
        """
        if not recompute and self.pos_reach_values is not None:
            return self.pos_reach_values

        self.get_safe(recompute)

        # Initialize:
        #  * safe_value for target states
        #  * inf otherwise
        self.pos_reach_values = [inf] * self.states

        for t in self.targets:
            self.pos_reach_values[t] = self.safe_values[t]

        largest_fixpoint(self.mdp, self.pos_reach_values,
                         self.action_value_T,
                         value_adj=self.reload_capper,
                         # Target states are always safe_values[t]
                         skip_state=lambda x: x in self.targets)
        return self.pos_reach_values

    def get_almostSureReachability(self, recompute=False):
        """Return (and compute) minimal levels for almost-sure
        reachability of `self.targets` and `self.capacity`.

        When called for the first time, compute the values.
        Recomputes the values if requested by `recompute`.

        A Bellman-style equation largest fixpoint solver.

        On the high level, it goes as:
          1. Compute Safe = Safe_M (achieved by get_safe())
          2. Repeat the following until fixpoint:
            2.1. Compute PosReach_M with modified Safe_M computation
            2.2. NonReach = {r is reload and PosReach_M[r] = ∞}
            2.3. M = M \ NonReach

        The PosReach_M is computed as:
          2.1.1. Compute modified Safe_M & store it in reach_safe_val
            - Safe_M[t] = Safe[t] for targets
            - Use fixpoint propagation to complete Safe_M
          2.1.3. PosReach_M[t] = Safe[t] for targets
          2.1.3. fixpoint that navigates to T (using Safe_M)

        This guarantees that after reaching T we have enough energy to
        survive. Until then we can always keep in states (and energy
        levels) with positive reachability of T. After T was reached,
        we can use the reloads not good enough for positive reachability
        again (Safe_M[t] = Safe[t]).

        The first iteration (the first fixpoint achieved) is equal
        to positive reachability.
        """
        if not recompute and self.alsure_values is not None:
            return self.alsure_values

        # removed stores reloads that had been removed from the MDP
        removed = set()

        done = False
        while not done:
            ### 2.1.1.
            # safe_after_T initializes each iteration of the fixpoint with:
            #  * self.safe_values[t] for targets (reach done, just survive)
            #  * ∞ for the rest
            safe_after_T = lambda s: self.safe_values[s] if s in self.targets else inf
            self.sufficient_levels(removed, self.reach_safe_val, safe_after_T)

            ### 2.1.2. Initialize PosReach_M:
            #  * safe_value for target states
            #  * inf otherwise
            self.alsure_values = [inf] * self.states
            for t in self.targets:
                self.alsure_values[t] = self.get_safe()[t]

            ### 2.1.3 Compute PosReach on sub-MDP
            # Mitigate reload removal (use Safe_M for survival)
            rem_survival_val = lambda s: self.reach_safe_val[s]
            rem_action_value = lambda a, v: self.action_value_T(a, v, rem_survival_val)

            # Avoid unnecesarry computations
            is_removed = lambda x: x in removed # always ∞
            is_target  = lambda x: x in self.targets # always Safe
            skip_cond  = lambda x: is_removed(x) or is_target(x)

            ## Finish the fixpoint
            largest_fixpoint(self.mdp, self.alsure_values,
                             rem_action_value,
                             value_adj=self.reload_capper,
                             skip_state=skip_cond)

            ### 2.2. & 2.3. Detect bad reloads and remove them
            done = True
            # Iterate over reloads and remove unusable ones (∞)
            for s in range(self.states):
                if self.is_reload(s) and self.alsure_values[s] == inf:
                    if s not in removed:
                        removed.add(s)
                        done = False

        return self.alsure_values

    def action_value_T(self, a, values, survival_val=None):
        """Compute value of action wtih preference and survival.

        The value picks a prefered target `t` that it wants to reach;
        considers `values` for `t` and `survival` for the other successors.
        Chooses the best (minimum) among possible `t` from `a.succs`.

        The value is cost of the action plus minimum of `v(t)` over
        t ∈ a.succs where `v(t)` is:
        ```
        max of {values(t)} ∪ {survival(t') | t' ∈ a.succ & t' ≠ t}
        ```
        where survival is given by `survival_val` vector. It's
        `self.safe_values` as default.

        Parameters
        ==========
        `a` : action_data, action for which the value is computed.
        `values` = vector with current values.
        `survival_val` = Function: `state` -> `value` interpreted as "what is
                         the level of energy I need to have in order to survive
                         if I reach `state`". Returns `self.safe_values[state]`
                         by default.
        """
        if survival_val is None:
            survival_val = lambda s: self.safe_values[s]

        # Initialization
        candidate = inf
        succs = a.distr.keys()

        for t in succs:
            # Compute value for t
            survivals = [survival_val(s) for s in succs if s != t]
            current_v = values[t]
            t_v = max([current_v] + survivals)

            # Choose minimum
            if t_v < candidate:
                candidate = t_v
            #print(f"{a.src} -- {a.label} -> {t}:{t_v}")
        return candidate + a.cons
