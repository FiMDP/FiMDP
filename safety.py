from math import inf

class minInitCons:
    """Compute function minInitCons for given consMDP `m`.
    
    minInitCons_m: S -> N ∪ {∞} returns for given `s` the minimum
    amount `s_m` of resource such that there exists a strategy that
    guarantees reachability of some reload state from s consuming
    at most `s_m`.
    
    Typical use:
    MI = minInitCons(mdp)
    MI.get_values()
    """

    def __init__(self, mdp):
        self.mdp     = mdp
        self.states  = mdp.num_states
        self.F       = [0] * self.states
        self.G       = [0] * self.states
        self.F_ready = False
        self.G_ready = False

    def action_F_value(self, a):
        non_reload_succs = [self.F[succ] for succ in a.distr.keys() 
                   if not self.mdp.is_reload(succ)]
        a_v = 0 if len(non_reload_succs) == 0 else max(non_reload_succs)
        return a_v + a.cons

    def fixpoint(self, func = "F"):
        """Computes the functional F (or G if requested).

        `func` can be either "F" or "G"

        !!! G should be always called after F !!!

        The functionals compute for each state `s` the maximum
        energy needed to reach a reload state from `s`.
        
        G detects increasing cycles by setting ∞ to states from
        which such cycle is reachable.
        """
        if func not in "FG":
            raise AttributeError(f'func has to be "F" or "G". {func} supplied')
        if func == "G" and not self.F_ready:
            raise AttributeError("G functional can be only called after F" +
                                 " is computed.")

        F = func == "F"

        values = self.F if F else self.G

        # iterate until a fixpoint is reached or for at most |S| steps
        iterate = True
        c = self.states      
        while iterate and c > 0:
            iterate = False
            c -= 1

            for s in range(self.states):
                current_v = values[s]
                actions = self.mdp.actions_for_state(s)
                # candidate_v is now the minimum over action values
                candidate_v = min([self.action_F_value(a) for a in actions])

                # F and G are monotonicly increasing, 
                # check for increase only
                if candidate_v > current_v:
                    values[s] = candidate_v if F else inf
                    iterate = True
        if F:
            self.F_ready = True
            # keep the F and G values separate
            self.G = list(values)
        else:
            self.G_ready = True

    def get_values(self, recompute=False):
        """Return (and compute) minInitCons list for self.m.
        
        When called for the first time, it computes the values.
        Recomputes the values if requested by `recompute`.
        """
        if recompute:
            self.F_ready, self.G_ready = False, False
            self.F = [0] * self.states
        if not self.F_ready:
            self.fixpoint("F")
        if not self.G_ready:
            self.fixpoint("G")
        return self.G
