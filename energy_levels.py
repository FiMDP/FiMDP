from math import inf
from sys import stderr
from fixpoints import largest_fixpoint, least_fixpoint

class EnergyLevels:
    """Compute minimum levels of energy needed to fulfill objectives
    with given capacity (and target set).

    For each objective `o` and each state `s`, compute a value `o[s]
    which guaranteed that there exists a strategy with fiven capacity
    that fulfills `o` from `s` and it needs `o[s]` to start with in `s`.
    
    Currently, the supported objectives are:
     * minInitCons: reaching a reload state different from `s`
     * safe       : survive from `s` forever
     * positiveReachability(T)  : survive and the probability of reaching
             some target from T is positive (>0)
     * almostSureReachability(T): survive and the probability of reaching
             some target from T is 1
     * Büchi(T) : survive and keep visiting T forever (with prob. 1).
    """

    def __init__(self, mdp, cap = inf, targets = None):
        # cap has to be defined
        if cap is None:
            cap = inf

        self.mdp         = mdp
        self.states      = mdp.num_states
        self.cap         = cap
        self.targets     = targets

        # minInitCons & Safe^cap
        self.mic_values  = None
        self.safe_values = None

        # Reachability
        self.pos_reach_values = None
        self.alsure_values = None

        # Buchi
        self.buchi_values = None

        # reloads
        self.is_reload  = lambda x: self.mdp.is_reload(x)

    ### Helper functions ###
    # * reload_capper     : [v]^cap
    # * action_value      : the worst value of succ(a) + cons(a)
    # * action_value_T    : directed action value
    # * sufficient_levels : inicialized safe values

    def _reload_capper(self, s, v):
        """Reloads with value < capacity should be 0,
        anything above capacity should be ∞
        """
        # +1 handles cases when self.cap is ∞
        if v >= self.cap+1:
            return inf
        if self.is_reload(s):
            return 0
        return v

    def _action_value(self, a, values, zero_cond = None):
        """
        - action    : `ActionData` action of MDP to evaluate
        - values    : `list of ints` current values
        - zero_cond : `list of Bool` if `True` for `s`, the
                       value of `s` will be trated as 0
        """
        if zero_cond is None:
            zero_cond = self.is_reload
        non_reload_succs = [values[succ] for succ in a.distr.keys()
                   if not zero_cond(succ)]
        a_v = 0 if len(non_reload_succs) == 0 else max(non_reload_succs)
        return a_v + a.cons

    def _action_value_T(self, a, values, survival_val=None):
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

    def _sufficient_levels(self, removed=None, values=None,
                          init_val=lambda s: inf):
        """Compute the safe_values using the largest-fixpoint method
        based on minInitCons computation with removal of reload states
        that have minInitCons() = ∞ in the previous itertions.

        The first computation computes, in fact, minInitCons (redundantly)

        The worst-case complexity is |R| * minInitCons = |R|*|S|^2

        `removed` : set of reloads - start with the reloads already removed
                    ∅ by default
        `values`  : list used for computation
                    self.safe_values as default
        `init_val`: state -> value - defines the values at the start of each
                    iteration of inner fixpoint (currently needed only for)
                    almost-sure reachability. It simulates switching between
                    the MDP with 2 sets of reload states (one before, one
                    [the original set R] after reaching T). 
        """
        if values is None:
            values = self.safe_values

        if removed is None:
            removed = set()

        done = False
        while not done:
            # Compute fixpoint without removed reloads

            # Reset the computation, by default set all values to ∞.
            # `init_val: s -> v
            for s in range(self.states):
                values[s] = init_val(s)

            # Mitigate reload removal
            zero_cond = lambda x: self.is_reload(x) and x not in removed
            rem_action_value = lambda a, v: self._action_value(a, v, zero_cond)

            # Removed reloads are skipped
            skip_cond = lambda x: x in removed # Improve performance only
            # Over capacity values -> ∞
            cap = lambda s, v: inf if v > self.cap else v

            largest_fixpoint(self.mdp, values,
                             rem_action_value,
                             value_adj=cap,
                             skip_state=skip_cond)

            done = True
            # Iterate over reloads and remove unusable ones (∞)
            for s in range(self.states):
                if self.is_reload(s) and values[s] == inf:
                    if s not in removed:
                        removed.add(s)
                        done = False

        # Set reload values to 0
        for s in range(self.states):
                if self.mdp.is_reload(s) and values[s] < self.cap:
                    values[s] = 0

    ### Public interface ###
    # * get_minInitCons
    # * get_safe
    # * get_positiveReachability
    # * get_almostSureReachability
    def get_minInitCons(self, recompute=False):
        """Return (and compute) minInitCons list for self.mdp.

        MinInitCons(s) is the maximal energy needed to reach reload.
        Computed by largest fixpoint that is reached within at most
        |S| iterations.

        If self.cap is set than treat values > self.cap as ∞.

        When called for the first time, compute the values.
        Recompute the values if requested by `recompute`.
        """
        if self.mic_values is None or recompute:
            self.mic_values = [inf] * self.states
            cap = lambda s, v: inf if v > self.cap else v
            largest_fixpoint(self.mdp, self.mic_values,
                             self._action_value,
                             value_adj=cap)
        return self.mic_values

    def get_safe(self, recompute=False):
        """Return (and compute) safe runs minimal cost for self.capacity

        When called for the first time, it computes the values.
        Recomputes the values if requested by `recompute`.
        """
        if self.safe_values is None or recompute:
            self.safe_values = [inf] * self.states
            self._sufficient_levels()

            # Set the value of Safe to 0 for all good reloads 
            for s in range(self.states):
                if self.mdp.is_reload(s) and self.safe_values[s] < self.cap:
                    self.safe_values[s] = 0
        return self.safe_values

    def get_positiveReachability(self, recompute=False):
        """Return (and compute) minimal levels for positive
        reachability of `self.targets` and `self.capacity`.

        When called for the first time, compute the values.
        Recomputes the values if requested by `recompute`.

        A Bellman-style equation largest fixpoint solver.

        We start with ∞ for every state and propagate the safe energy
        needed to reach T from the target states further. Use
        `action_value_T` for computing the value of an action.
        Basically, it chooses the best a-successor `t`. The value
        of this successor is the energy needed to safely reach T via this
        successor + the safe energy level from the possibly-reached target
        state, or the energy needed to survive in some other successor
        under the action, whatever is higher.
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
                         self._action_value_T,
                         value_adj=self._reload_capper,
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
          2.1.1. Compute modified Safe_M & store it in reach_safe
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

        # Initialize the helper values
        self.reach_safe = [inf] * self.states

        # Initialized safe values after reaching T
        self.get_safe()
        safe_after_T = lambda s: self.safe_values[s] if s in self.targets else inf

        done = False
        while not done:
            ### 2.1.1.
            # safe_after_T initializes each iteration of the fixpoint with:
            #  * self.safe_values[t] for targets (reach done, just survive)
            #  * ∞ for the rest

            self._sufficient_levels(removed, self.reach_safe, safe_after_T)

            ### 2.1.2. Initialize PosReach_M:
            #  * safe_value for target states
            #  * inf otherwise
            self.alsure_values = [inf] * self.states
            for t in self.targets:
                self.alsure_values[t] = self.get_safe()[t]

            ### 2.1.3 Compute PosReach on sub-MDP
            # Mitigate reload removal (use Safe_M for survival)
            rem_survival_val = lambda s: self.reach_safe[s]
            rem_action_value = lambda a, v: self._action_value_T(a, v, rem_survival_val)

            # Avoid unnecesarry computations
            is_removed = lambda x: x in removed # always ∞
            is_target  = lambda x: x in self.targets # always Safe
            skip_cond  = lambda x: is_removed(x) or is_target(x)

            ## Finish the fixpoint
            largest_fixpoint(self.mdp, self.alsure_values,
                             rem_action_value,
                             value_adj=self._reload_capper,
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

        # Initialize the helper values
        self.buchi_safe = [inf] * self.states

        done = False
        while not done:
            ### 1.1. Compute Safe(M\removed) and store it in buchi_safe
            self._sufficient_levels(removed, self.buchi_safe)

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
            rem_action_value = lambda a, v: self._action_value_T(a, v, rem_survival_val)

            ## Avoid unnecessary computations
            is_removed = lambda x: x in removed # always ∞
            is_target  = lambda x: x in self.targets # always Safe_M
            skip_cond  = lambda x: is_removed(x) or is_target(x)

            ## Finish the fixpoint
            largest_fixpoint(self.mdp, self.buchi_values,
                             rem_action_value,
                             value_adj=self._reload_capper,
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



class EnergyLevels_least(EnergyLevels):
    """Variant of EnergyLevels class that uses (almost)
    least fixpoint to compute Safe values.

    The worst case number of iterations is c_max * |S|
    and thus the worst case complexity is

    ```
    c_max * |S|^2
    ```

    steps. The worst case complexity of the largest
    fixpoint version is |S|^2 iterations and thus
    |S|^3 steps.
    """

    def get_safe(self, recompute=False):
        """Return (and compute) safe runs minimal cost for
        self.capacity using the iteration from minInitCons
        towards an higher fixpoint.

        When called for the first time, it computes the values.
        Recomputes the values if requested by `recompute`.
        """
        if self.safe_values is None or recompute:
            self.safe_values = list(self.get_minInitCons(recompute))
            cap = lambda s, v: inf if v > self.cap else v
            # The +1 trick handels cases when cap=∞
            zero_c = lambda succ: (self.mdp.is_reload(succ) and \
                                  self.safe_values[succ] < self.cap+1)

            action_value = lambda a, values: self._action_value(a, values, zero_c)

            least_fixpoint(self.mdp, self.safe_values,
                             action_value,
                             value_adj=cap)

            # Set the value of Safe to 0 for all good reloads
            for s in range(self.states):
                if self.mdp.is_reload(s) and self.safe_values[s] < self.cap:
                    self.safe_values[s] = 0
        return self.safe_values
