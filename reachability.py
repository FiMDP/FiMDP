from safety import minInitCons, largest_fixpoint
from math import inf
class Reachability(minInitCons):
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
        super(Reachability, self).__init__(mdp, cap)

        self.targets = targets
        self.pos_reach_values = None

    def get_positiveReachability(self, recompute=False):
        """Return (and compute) minimal levels for positive
        reachability of `self.targets` and `self.capacity`.

        When called for the first time, it computes the values.
        Recomputes the values if requested by `recompute`.

        A Bellman-style equation largest fixpoint solver.

        We start with ∞ for every state and propagate the safe energy
        needed to reach T from the target states further.
        """
        if not recompute and self.pos_reach_values is not None:
            return self.pos_reach_values

        self.get_safe_values(recompute)

        # Reloads with value < ∞ should be 0
        def reload_capper(s, v):
            # +1 handles cases when self.cap is ∞
            if v >= self.cap+1:
                return inf
            if self.is_reload(s):
                return 0
            return v

        # Initialize:
        #  * safe_value for target states
        #  * inf otherwise
        self.pos_reach_values = [inf] * self.states

        for t in self.targets:
            self.pos_reach_values[t] = self.safe_values[t]

        largest_fixpoint(self.mdp, self.pos_reach_values,
                         self.action_value_T,
                         value_adj=reload_capper,
                         # Target states are always safe_values[t]
                         skip_state=lambda x: x in self.targets)
        return self.pos_reach_values

    def action_value_T(self, a, values):
        """Compute value of action basd on curent values pf `r`

        `target_values` = array with values that applies for `r(t)` if `t`
                          satisfies `target_cond`. Equal to self.safe_values
                          if not given.
        """
        # Initialization
        candidate = inf
        succs = a.distr.keys()

        for t in succs:
            survivals = [self.safe_values[s] for s in succs if s != t]
            current_v = values[t]
            t_v = max([current_v] + survivals)

            if t_v < candidate:
                candidate = t_v
            #print(f"{a.src} -- {a.label} -> {t}:{t_v}")
        return candidate + a.cons
