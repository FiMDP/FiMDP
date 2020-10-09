from .core import ConsMDP, ActionData
from .objectives import *

from math import inf


class Duplicator:
    """
    Makes an independent (deep) copy of the given consMDP.

    The `max_states` parameter is used to limit the number of states
    that will be used in the new mdp. If set and used, the resulting
    ConsMDP will have the `.incomplete` attribute which stores the
    set of states whose successors could not be fully built.

    The function starts building the copy from the init_state and
    builds only the part reachable from this state
    """

    def __init__(self, mdp: ConsMDP, init_state=0,
                 max_states=inf, preserve_names=True,
                 solver=None):
        self.mdp = mdp
        self.out = ConsMDP()

        self.preserve_names = preserve_names
        self.max_states = max_states

        self.incomplete = set()
        self.out.incomplete = self.incomplete

        self.seen = {}
        self.todo = []
        self._new_state(init_state)

    def _new_state(self, s):
        if s not in self.seen:
            if self.preserve_names and self.mdp.names[s] is not None:
                name = self.mdp.names[s]
            else:
                name = str(s)
            p = self.out.new_state(reload=self.mdp.is_reload(s), name=name)
            self.seen[s] = p
            self.todo.append((s, p))
            return p
        else:
            return self.seen[s]

    def run(self):
        while self.todo:
            src1, src2 = self.todo.pop(0)
            action : ActionData
            for action in self.mdp.actions_for_state(src1):
                # Gather newly created states
                new_succs = [s for s in action.distr if s not in self.seen]
                # If the max states would be reached, do not create any
                # new states and action
                if len(new_succs) + self.out.num_states > self.max_states:
                    self.incomplete.add(src2)
                    continue

                distr = {self._new_state(succ) : p for succ, p in
                         action.distr.items()}
                action_num = self.out.add_action(src2, distr,
                                                 action.label, action.cons)


def copy_consmdp(mdp, init_state=0,
                 max_states=inf, preserve_names=True,
                 solver=None):
    duplicator = Duplicator(mdp, init_state, max_states, preserve_names, solver)
    duplicator.run()
    return duplicator.out, duplicator.seen