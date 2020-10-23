"""Module with energy-aware qualitative solvers for Consumption MDPs

Currently, the supported objectives are:
 * minInitCons: reaching a reload state within >0 steps
 * safe       : survive from `s` forever
 * positiveReachability(T)  : survive and the probability of reaching
         some target from T is positive (>0)
 * almostSureReachability(T): survive and the probability of reaching
         some target from T is 1
 * Büchi(T) : survive and keep visiting T forever (with prob. 1).

The results of a solver for an objective `o` are twofolds:
 1. For each state `s` we provide value `o[s]` which is the minimal initial
    load of energy needed to satisfy the objective `o` from `s`.
 2. Corresponding strategy that, given at least `o[s]` in `s` guarantees that
    `o` is satisfied.

The computed values `o[s]` from 1. can be visualized in the `mdp` object by
setting `mdp.EL=solver` and then calling `mdp.show()`.
"""

from math import inf
from sys import stderr

from .core import CounterSelector
from .objectives import MIN_INIT_CONS, SAFE, POS_REACH, AS_REACH, BUCHI
from .objectives import _HELPER_AS_REACH, _HELPER_BUCHI, _OBJ_COUNT

### HELPER objectives ###

# Control debug info printed after fixpoints iterations
debug = False
debug_vis = False


class BasicES:
    """Solve qualitative objectives for Consumption MDPs.

    This implements the algorithms as described in the paper
    Qualitative Controller Synthesis for Consumption Markov Decision Processes

    Parameters
    ==========
     * mdp: `ConsMDP` object
     * cap: `int`; energy capacity for given objective
     * targets: `iterable`; states of `mdp` that are targets for the objectives.
    """

    def __init__(self, mdp, cap, targets):
        self.mdp         = mdp
        self.states      = mdp.num_states
        self.cap         = cap
        self.targets     = targets

        self.min_levels = {}
        self.helper_levels = {}

        # reloads
        self.is_reload  = lambda x: self.mdp.is_reload(x)

        # Selector's setup
        self.strategy = {}
        self.SelectorClass = CounterSelector

        # HOOKS
        # Hooks that enable creation of heuristic-based child classes.
        # IMPORTANT: these are only used in reachability objectives,
        # not safety.
        #
        # Initialization of argmin function for fixpoint computations.
        self.argmin = argmin
        # Function that computes largest fixpoint
        self.largest_fixpoint = largest_fixpoint

        # Debug hooks used to visualize or print intermediate
        # results in fixpoints
        self.debug = False # prints
        self.debug_vis = False # calls self.show()

    ### Helper functions ###
    # * reload_capper     : [v]^cap
    # * action_value      : the worst value of succ(a) + cons(a)
    # * action_value_T    : directed action value
    # * sufficient_levels : inicialized safe values
    # * init_strategy     : initializes an empty strategy for given objective
    # * copy_strategy     : copy strategy on given states from one strategy to another
    # * update_function   : return function that updates strategy for given objective (or does nothing)

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

        The value picks a preferred target `t` that it wants to reach;
        considers `values` for `t` and `survival` for the other successors.
        Chooses the best (minimum) among possible `t` from `a.succs`.

        The value is cost of the action plus minimum of `v(t)` over
        t ∈ a.succs where `v(t)` is:
        ```
        max of {values(t)} ∪ {survival(t') | t' ∈ a.succ & t' ≠ t}
        ```
        where survival is given by `survival_val` vector. It's
        `self.min_levels[SAFE]` as default.

        Parameters
        ==========
        `a` : action_data, action for which the value is computed.
        `values` = vector with current values.
        `survival_val` = Function: `state` -> `value` interpreted as "what is
                         the level of energy I need to have in order to survive
                         if I reach `state`". Returns `self.min_levels[SAFE][state]`
                         by default.
        """
        if survival_val is None:
            survival_val = lambda s: self.min_levels[SAFE][s]

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

    def _sufficient_levels(self, values,
                           removed=None,
                           init_val=lambda s: inf,
                           objective=SAFE):
        """Compute the survival values.

        Use the largest-fixpoint method based on minInitCons computation with
        removal of reload states that have minInitCons() = ∞ in the previous
        iteration. After the last iteration, the computed strategy (and minimal
        levels) are enough to survive in the mdp ad infinitum.

        If `init_val` is given, the semantics is slightly different: _Survive
        ad infinitum or reach one of the states `s` for which `init_val[s]<∞`
        with at least `init_val[s]` energy.

        The first computation computes, in fact, minInitCons (redundantly)

        The worst-case complexity is |R| * minInitCons = |R|*|S|^2

        `values`  : list used for computation
                    self.min_levels[SAFE] as default
        `removed` : set of reloads - start with the reloads already removed
                    ∅ by default
        `init_val`: state -> value - defines the values at the start of each
                    iteration of inner fixpoint. This simulates switching between
                    the MDP with 2 sets of reload states (one before, one
                    [the original set R] after reaching T).
        `objective`:objective for which computes the strategy (SAFE by default)
        """
        if values is None:
            values = self.min_levels[SAFE]

        if removed is None:
            removed = set()

        done = False
        while not done:
            # Compute fixpoint without removed reloads
            self._init_strategy(objective)

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

            largest_fixpoint(self, values,
                             rem_action_value,
                             value_adj=cap,
                             skip_state=skip_cond,
                             on_update=self._update_function(objective))

            done = True
            # Iterate over reloads and remove unusable ones (∞)
            for s in range(self.states):
                if self.is_reload(s) and values[s] == inf:
                    if s not in removed:
                        removed.add(s)
                        done = False

        # Set reload values to 0, "< & +1"-trick to handle ∞
        for s in range(self.states):
                if self.mdp.is_reload(s) and values[s] < self.cap+1:
                    values[s] = 0

    def _init_strategy(self, objective):
        """Initialize strategy for given objective to be empty.

        The empty strategy is a list with an empty dict for each state.
        """
        self._check_objective(objective, True)
        self.strategy[objective] = self.SelectorClass(self.mdp)

    def _copy_strategy(self, source, to, state_set=None):
        """Copy strategy for objective `source` to objective `to` for states in `states_set`

        Parameters:
        ===========
        `source` : int, index of objective to copy from
        `to`     : int, index of objective to copy to
        `state_set` : set of states for which to copy the strategy
                       -- all states by default
        """
        if state_set is None:
            state_set = range(self.states)

        self._check_objective(source, helper=True)
        self._check_objective(to)

        self.strategy[to].copy_values_from(self.strategy[source], state_set)

    def _update_function(self, objective):
        """Return update function for given objective.

        Returns function that should be passed to `largest_fixpoint` to
        update strategy for given objective.
        """
        self._check_objective(objective, helper=True)

        def update(s, e, a):
            self.strategy[objective].update(s, e, a)

        return update

    ### Functions for running the computations for objectives ###
    # * _minInitCons
    # * _safe
    # * _positive_reachability
    # * _almost_sure_reachability
    # * _buchi
    def _minInitCons(self):
        """
        Compute MIN_INIT_CONS selector and min_levels.

        Use largest fixpoint that is reached within at most `|S|` iterations.
        Treat values > self.cap as ∞.
        """
        self._init_strategy(MIN_INIT_CONS)

        self.min_levels[MIN_INIT_CONS] = [inf] * self.states
        cap = lambda s, v: inf if v > self.cap else v
        largest_fixpoint(self,
                         self.min_levels[MIN_INIT_CONS],
                         self._action_value,
                         value_adj=cap,
                         on_update=self._update_function(MIN_INIT_CONS))

    def _safe(self):
        """
        Compute SAFE selector and min_levels.

        Use largest fixpoint. Min_levels are 0 in reloading states.
        """
        objective = SAFE
        self._init_strategy(objective)

        self.min_levels[SAFE] = [inf] * self.states
        self._sufficient_levels(self.min_levels[SAFE], objective=SAFE)

        # Set the value of Safe to 0 for all good reloads
        for s in range(self.states):
            if self.mdp.is_reload(s) and self.min_levels[SAFE][s] < self.cap+1:
                self.min_levels[SAFE][s] = 0

    def _positive_reachability(self):
        """
        Compute POS_REACH selector and min_levels.

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
        objective = POS_REACH
        self._init_strategy(objective)

        # Initialize:
        #  * safe_value for target states
        #  * inf otherwise
        if SAFE not in self.min_levels:
            self.compute(SAFE)
        self.min_levels[POS_REACH] = [inf] * self.states

        for t in self.targets:
            self.min_levels[POS_REACH][t] = self.min_levels[SAFE][t]

        self.largest_fixpoint(self, self.min_levels[POS_REACH],
                         self._action_value_T,
                         value_adj=self._reload_capper,
                         # Target states are always min_levels[SAFE][t]
                         skip_state=lambda x: x in self.targets,
                         on_update=self._update_function(objective),
                         argmin=self.argmin)

        self._copy_strategy(SAFE, objective, self.targets)

    def _almost_sure_reachability(self):
        """
        Compute AS_REACH selector and min_levels.

        A Bellman-style equation largest fixpoint solver.

        On the high level, it goes as:
          1. Compute Safe = Safe_M (achieved by get_min_levels(SAFE))
          2. Repeat the following until fixpoint:
            2.1. Compute PosReach_M with modified Safe_M computation
            2.2. NonReach = {r is reload and PosReach_M[r] = ∞}
            2.3. M = M \ NonReach

        The PosReach_M is computed as:
          2.1.1. Compute modified Safe_M & store it in helper_levels[AS_REACH]
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
        objective = AS_REACH
        # removed stores reloads that had been removed from the MDP
        removed = set()

        # Initialize the helper values
        self.helper_levels[AS_REACH] = [inf] * self.states

        # Initialized safe values after reaching T
        if SAFE not in self.min_levels:
            self.compute(SAFE)
        safe_after_T = lambda s: self.min_levels[SAFE][s] \
            if s in self.targets \
            else inf

        done = False
        while not done:
            ### 2.1.1.
            # safe_after_T initializes each iteration of the fixpoint with:
            #  * self.min_levels[SAFE][t] for targets (reach done, just survive)
            #  * ∞ for the rest

            self._sufficient_levels(self.helper_levels[AS_REACH], removed, safe_after_T,
                                    _HELPER_AS_REACH)

            ### 2.1.2. Initialize PosReach_M:
            #  * safe_value for target states
            #  * inf otherwise
            self.min_levels[AS_REACH] = [inf] * self.states
            for t in self.targets:
                self.min_levels[AS_REACH][t] = self.get_min_levels(SAFE)[t]

            self._init_strategy(objective)

            ### 2.1.3 Compute PosReach on sub-MDP
            # Mitigate reload removal (use Safe_M for survival)
            rem_survival_val = lambda s: self.helper_levels[AS_REACH][s]
            rem_action_value = lambda a, v: self._action_value_T(a, v, survival_val=rem_survival_val)

            # Avoid unnecessary computations
            is_removed = lambda x: x in removed  # always ∞
            is_target = lambda x: x in self.targets  # always Safe
            skip_cond = lambda x: is_removed(x) or is_target(x)

            ## Finish the fixpoint
            self.largest_fixpoint(self, self.min_levels[AS_REACH],
                             rem_action_value,
                             value_adj=self._reload_capper,
                             skip_state=skip_cond,
                             on_update=self._update_function(objective),
                             argmin=self.argmin)

            ### 2.2. & 2.3. Detect bad reloads and remove them
            done = True
            # Iterate over reloads and remove unusable ones (∞)
            for s in range(self.states):
                if self.is_reload(s) and self.min_levels[AS_REACH][s] == inf:
                    if s not in removed:
                        removed.add(s)
                        done = False

            self._copy_strategy(SAFE, objective, self.targets)

    def _buchi(self):
        """
        Compute BUCHI selector and min_levels.

        A Bellman-style equation largest fixpoint solver.

        On the high level, repeat following until fixpoint:
          1. compute PosReach_M
          2. NonReach = {r is reload and PosReach_M[r] = ∞}
          3. M = M \ NonReach

        The PosReach_M is computed as:
          1.1. Safe_M (largest_fixpoint)
          1.2. PosReach_M[t] = Safe_M[t] for targets
          1.3. fixpoint that navigates to T

        This guarantees that we can always keep in states that
        have positive probability of reaching T and that we can
        always eventually reach energy sufficient to navigate
        towards T.

        In contrast to `almostSureReachability` here we do not set the
        `helper_levels[BUCHI]` values of targets to `min_levels[SAFE]` after
        each iteration. This si because after reaching a target, we still
        need to reach target again. So the steps 1.1 and 1.2 slightly differ.
        Otherwise, the computation is the same.

        The first iteration (the first fixpoint achieved) is equal
        to positive reachability.
        """
        objective = BUCHI

        # removed stores reloads that had been removed from the MDP
        removed = set()

        # Initialize the helper values
        self.helper_levels[BUCHI] = [inf] * self.states

        done = False
        while not done:
            ### 1.1. Compute Safe(M\removed) and store it in helper_levels[BUCHI]
            self._sufficient_levels(self.helper_levels[BUCHI], removed, objective=_HELPER_BUCHI)

            ### 1.2. Initialization of PosReach_M
            #  * helper_levels[BUCHI] for target states
            #  * inf otherwise
            self.min_levels[BUCHI] = [inf] * self.states
            for t in self.targets:
                self.min_levels[BUCHI][t] = self.helper_levels[BUCHI][t]

            self._init_strategy(objective)

            ### 1.3. Computation of PosReach on sub-MDP (with removed reloads)
            ## how much do I need to survive via this state after reloads removal
            # Use Safe_m (stored in helper_levels[BUCHI]) as value needed for survival
            rem_survival_val = lambda s: self.helper_levels[BUCHI][s]
            # Navigate towards T and survive with Safe_m
            rem_action_value = lambda a, v: self._action_value_T(a, v, survival_val=rem_survival_val)

            ## Avoid unnecessary computations
            is_removed = lambda x: x in removed  # always ∞
            is_target = lambda x: x in self.targets  # always Safe_M
            skip_cond = lambda x: is_removed(x) or is_target(x)

            ## Finish the fixpoint
            self.largest_fixpoint(self, self.min_levels[BUCHI],
                                  rem_action_value,
                                  value_adj=self._reload_capper,
                                  skip_state=skip_cond,
                                  on_update=self._update_function(BUCHI),
                                  argmin=self.argmin)

            ### 2. & 3. Detect bad reloads and remove them
            done = True
            # Iterate over reloads and remove unusable ones (∞)
            for s in range(self.states):
                if self.is_reload(s) and self.min_levels[BUCHI][s] == inf:
                    if s not in removed:
                        removed.add(s)
                        done = False

            self._copy_strategy(_HELPER_BUCHI, BUCHI, self.targets)


    def _check_objective(self, objective, helper=False):
        upper_bound = _OBJ_COUNT if helper else BUCHI + 1
        if not 0 <= objective < upper_bound:
            raise ValueError(f"Objective must be between 0 and {upper_bound - 1}."
                             f" {objective} was given!")

    ### Public interface ###
    # * compute
    # * get_min_levels
    # * get_selector
    def compute(self, objective):
        self._check_objective(objective)
        func_dict = {
            MIN_INIT_CONS: self._minInitCons,
            SAFE:          self._safe,
            POS_REACH:     self._positive_reachability,
            AS_REACH:      self._almost_sure_reachability,
            BUCHI:         self._buchi,
        }
        func_dict[objective]()


    def get_min_levels(self, objective, recompute=False):
        """
        Return minimal levels required to satisfy `objective`

        Parameters
        ==========
        `objective` : one of MIN_INIT_CONS, SAFE, POS_REACH, AS_REACH, BUCHI
        `recompute` : if `True` forces all computations to be done again
        """
        self._check_objective(objective)
        if recompute or objective not in self.min_levels:
            self.compute(objective)

        return self.min_levels[objective]

    def get_selector(self, objective, recompute=False):
        """Return (and compute) strategy such that it ensures it can handle
        the minimal levels of energy required to satisfy given objective
        from each state (if < ∞).

        `objective` : one of MIN_INIT_CONS, SAFE, POS_REACH, AS_REACH, BUCHI
        `recompute` : if `True` forces all computations to be done again
        """
        self._check_objective(objective)
        if recompute or objective not in self.strategy:
            self.compute(objective)
        return self.strategy[objective]

    def get_dot (self, options=""):
        from . import dot
        dot_writer = dot.consMDP2dot(mdp=self.mdp, solver=self, options=options)
        return dot_writer.get_dot()

    def _repr_svg_(self):
        from . import dot
        return dot.dot_to_svg(self.get_dot(), mdp=self.mdp)

    def show(self, options="", max_states=None):
        from IPython.display import SVG
        from . import dot
        if max_states is not None:
            options += f".<{max_states}"
        return SVG(dot.dot_to_svg(self.get_dot(options), mdp=self.mdp))


class GoalLeaningES(BasicES):
    """Solver that prefers actions leading to target with higher probability.

    This class extends `BasicES` (implementation of CAV'2020 algorithms)
    by a heuristic that make the strategies more useful for control. The main
    goal of this class is to create strategies that go to targets quickly.

    The solver modifies only the computation of positive reachability computation.

    Among action that achieves the minimal _action_value_T, choose the one with
    the highest probability of hitting the picked successor. The modification is
    twofold:
     1. redefine _action_value_T
     2. instead of classical argmin, use pick_best_action that works on tuples
        (value, probability of hitting good successor).

    See more technical description in docstring for _action_value_T.

    If threshold is set to value > 0, then we also modify how fixpoint works:
     3. Use 2-shot fixpoint computations for positive reachability; the first
        run ignores successors that can be reached with probability < threshold.
        The second fixpoint is run with threshold=0 to cover the cases where the
        below-threshold outcomes only would lead to higher initial loads.

    Parameters
    ==========
     * mdp: `ConsMDP` object
     * cap: `int`; energy capacity for given objective
     * targets: `iterable`; states of `mdp` that are targets for the objectives.
     * threshold: `float`, default 0; a probability treshold.
                  Successor less likely then `treshold` will be ignored
                  in the first fixpoint.
    """

    def __init__(self, mdp, cap, targets=None, threshold=0):
        super().__init__(mdp=mdp, cap=cap, targets=targets)
        self.threshold = threshold
        self.argmin = pick_best_action
        self.largest_fixpoint = self.double_fixpoint

    def _action_value_T(self, a, values, survival_val=None, threshold=None):
        """Compute value of action with preference and survival.

        Return also the probability with which the action can lead to the
        picked successor. Disregards successors whose probability of being
        chosen is below the given threshold. Among successors with the same
        value pick the largest probability.

        The value picks a preferred target `t` that it wants to reach;
        considers `values` for `t` and `survival` for the other successors.
        Chooses the best (minimum) among possible `t` from `a.succs`.

        The value is cost of the action plus minimum of `v(t)` over
        t ∈ a.succs where `v(t)` is:
        ```
        max of {values(t)} ∪ {survival(t') | t' ∈ a.succ & t' ≠ t}
        ```
        where survival is given by `survival_val` vector. It's
        `self.min_levels[SAFE]` as default.

        Parameters
        ==========
        `a` : action_data, action for which the value is computed.
        `values` = vector with current values.
        `survival_val` = Function: `state` -> `value` interpreted as "what is
                         the level of energy I need to have in order to survive
                         if I reach `state`". Returns `self.min_levels[SAFE][state]`
                         by default.

        Returns
        =======
        `(action_value, prob)` where `action_value` is the value of the action
                        and `prob` is the probability that the action would
                        go to the picked successor that enables this value.
        """
        if threshold is None:
            threshold = self.threshold
        if survival_val is None:
            survival_val = lambda s: self.min_levels[SAFE][s]

        # Initialization
        candidate = inf
        prob = 0
        succs = a.distr.keys()

        for t in succs:
            t_p = a.distr[t] # Likelihood of t being the outcome

            if t_p < threshold:
                continue
            # Compute value for t
            survivals = [survival_val(s) for s in succs if s != t]
            current_v = values[t]
            t_v = max([current_v] + survivals)

            # Choose minimum
            if t_v < candidate or (t_v == candidate and t_p > prob):
                candidate = t_v
                prob = t_p
            # print(f"{a.src} -- {a.label} -> {t}:{t_v}")
        return candidate + a.cons, prob

    def double_fixpoint(self, *args, **kwargs):
        # First fixpoint using threshold
        largest_fixpoint(*args, **kwargs)

        # Second fixpoint with threshold=0
        if self.threshold > 0:
            threshold = self.threshold # remember original value
            self.threshold = 0
            largest_fixpoint(*args, **kwargs)
            self.threshold = threshold


class LeastFixpointES(BasicES):
    """Solver that uses (almost) least fixpoint to compute Safe values.

    The worst case number of iterations is c_max * ``|S|``
    and thus the worst case complexity is ``c_max * |S|^2``
    steps. The worst case complexity of the largest
    fixpoint version is ``|S|``^2 iterations and thus
    ``|S|``^3 steps.
    """

    def _safe(self):
        """Compute the survival objective

        Uses least-fixpoint iteration from minInitCons towards an higher fixpoint.
        """
        self.min_levels[SAFE] = list(self.get_min_levels(MIN_INIT_CONS))
        cap = lambda s, v: inf if v > self.cap else v
        # The +1 trick handels cases when cap=∞
        zero_c = lambda succ: (self.mdp.is_reload(succ) and \
                               self.min_levels[SAFE][succ] < self.cap+1)

        action_value = lambda a, values: self._action_value(a, values, zero_c)

        least_fixpoint(self, self.min_levels[SAFE],
                       action_value,
                       value_adj=cap)

        # Set the value of Safe to 0 for all good reloads
        for s in range(self.states):
            if self.mdp.is_reload(s) and self.min_levels[SAFE][s] < self.cap+1:
                self.min_levels[SAFE][s] = 0


### argmin-style functions
# argmin
# pick_best_action
def argmin(items, func):
    """
    Compute argmin of func on iterable `items`.

    Returns (i, v) such that v=func(i) is smallest in `items`.
    """

    res_item, res_val = None, inf
    for item in items:
        val = func(item)
        if val < res_val:
            res_item, res_val = item, val

    return res_item, res_val


def pick_best_action(actions, func):
    """Compositional argmin and argmax.

    Given `func` of type `action → value × prob`, choose action
    that achieves the lowest `value` with the highest probability
    over actions with the same value. Which is, choose action
    with the lowest d=(`value`, 1-`prob`) using lexicographic
    order.
    """
    res_item, res_val, res_prob = None, inf, 0
    for item in actions:
        val, prob = func(item)
        if val < res_val or (val == res_val and prob > res_prob):
            res_item, res_val, res_prob = item, val, prob

    return res_item, res_val


### FIXPOINTS ###
def largest_fixpoint(solver, values, action_value,
                     value_adj=lambda s, v: v,
                     skip_state=lambda x: False,
                     on_update=lambda s, v, a: None,
                     argmin=argmin):
    """Largest fixpoint on list of values indexed by states.

    Most of the computations of energy levels are, in the end,
    using this function in one way or another.

    The value of a state `s` is a minimum over `action_value(a)`
    among all possible actions `a` of `s`. Values should be
    properly initialized (to ∞ or some other value) before calling.

    Parameters
    ==========
     * mdp      : `consMDP`
     * values   : `list of ints` values for the fixpoint

     * action_value : function that computes a value of an action
                      based on current values in `values`. Takes
                      2 paramers:
        - action    : `ActionData` action of MDP to evaluate
        - values    : `list of ints` current values

     * functions that alter the computation:
       - value_adj : `state × v -> v'` (default `labmda x, v: v`)
                      Change the value `v` for `s` to `v'` in each
                      iteration (based on the candidate value).
                      For example use for `v > capacity -> ∞`
                      Allows to handle various types of states
                      in a different way.

       - skip_state : `state -> Bool` (default `lambda x: False`)
                      If True, stave will be skipped and its value
                      not changed.

       - argmin : function that chooses which action to pick

     * on_upadate : function called when new value for state is found.
                    Arguments are: state × value × action
                    The meaning is for `s` we found new value `v` using
                    action `a`.
                    By default only None is returned.

    Debug options
    =============
    We have 2 options that help us debug the code using this function.
    These should be turned on in the respective solver:
     * `debug`     : print `values` at start of each iteration
     * `debug_vis` : display `mdp` using the IPython `display`
    """
    mdp = solver.mdp
    states = len(values)
    act_value = lambda a: action_value(a, values)

    # iterate until a fixpoint is reached
    iterate = True
    c = 0
    while iterate:
        if solver.debug: print(f"it {c}\t:{values}", file=stderr)
        if solver.debug_vis:
            from IPython.display import display
            display(f"Iteration {c}:", solver.show(".mspRB"))
        c += 1
        iterate = False

        for s in range(states):
            if skip_state(s):
                continue
            current_v = values[s]
            actions = mdp.actions_for_state(s)

            # candidate_v is the minimum over action values
            candidate_a, candidate_v = argmin(actions, act_value)

            # apply value_adj (capacity, reloads, ...)
            candidate_v = value_adj(s, candidate_v)

            # check for decrease in value
            if candidate_v < current_v:
                values[s] = candidate_v
                on_update(s, candidate_v, candidate_a)
                iterate = True


def least_fixpoint(solver, values, action_value,
                     value_adj=lambda s, v: v,
                     skip_state=None):
    """Least fixpoint on list of values indexed by states.

    The value of a state `s` is a minimum over `action_value(a)`
    among all posible actions `a` of `s`. Values should be
    properly initialized (to ∞ or some other value) before calling.

    For safe values the values should be initialized to
    minInitCons.

    Parameters
    ==========
     * solver   :  solver that calls the fixpoint (for visualisation only)
     * values   : `list of ints` values for the fixpoint

     * action_value : function that computes a value of an action
                      based on current values in `values`. Takes
                      2 paramers:
        - action    : `ActionData` action of MDP to evaluate
        - values    : `list of ints` current values

     * functions that alter the computation:
       - value_adj : `state × v -> v'` (default `labmda x, v: v`)
                      Change the value `v` for `s` to `v'` in each
                      iteration (based on the candidate value).
                      For example use for `v > capacity -> ∞`
                      Allows to handle various types of states
                      in a different way.

       - skip_state : `state -> Bool`
                      (default `lambda x: values[x] == inf`)
                      If True, stave will be skipped and its value
                      not changed.

    Debug options
    =============
    We have 2 options that help us debug the code using this function:
     * `debug`     : print `values` at start of each iteration
     * `debug_vis` : display `mdp` using the IPython `display`
    """
    mdp = solver.mdp
    if skip_state is None:
        skip_state = lambda x: values[x] == inf

    states = len(values)
    act_value = lambda a: action_value(a, values)

    # terate until a fixpoint is reached
    iterate = True
    c = 0
    while iterate:
        if solver.debug: print(f"it {c}\t:{values}", file=stderr)
        if solver.debug_vis:
            from IPython.display import display
            display(f"Iteration {c}:", solver.show(".mspRB"))
        c += 1
        iterate = False

        for s in range(states):
            if skip_state(s):
                continue

            current_v = values[s]
            actions = mdp.actions_for_state(s)
            # candidate_v is now the minimum over action values
            candidate_v = min([act_value(a) for a in actions])

            # apply value_adj (capacity, reloads, ...)
            candidate_v = value_adj(s, candidate_v)

            # least fixpoint increases only
            if candidate_v > current_v:
                values[s] = candidate_v
                iterate = True
