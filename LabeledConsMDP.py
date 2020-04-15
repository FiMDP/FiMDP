from consMDP import ConsMDP
from products import product_dba

from copy import deepcopy


class LCMDP(ConsMDP):
    """Represent consumption MDP with states labeled by sets of Atomic
    Propositions (AP).

    See the docs for ConsMDP for important notes about how to use this
    class in general. We only discuss labeling here.

    The states can now carry both labels with the meaning as name and
    the semantics labels with atomic propositions.

    The set of Atomic propositions that can be used in the labels is
    stored in list `LCMDP.AP`. The list also establishes a mapping
    from ints to APs. The dict `LCMDP.AP2int` translates the APs into
    numbers that are actually used for the labels.

    The labeling function is implemented as a list `LCMDP.state_labels`.
    Complementary, all states with the given set of AP can be obtained
    by`LCMDP.get_states_with_label()`. The state labels are sets of
    integers that correspond to intended APs.

    Parameters:
    ===========
      * AP : list of names of atomic propositions
    """

    def __init__(self, AP, mdp=None):
        if mdp is None:
            ConsMDP.__init__(self)
        else:
            self._copy_mdp(mdp)
        self._init_AP(AP)

    def _init_AP(self, AP):
        # Mapping of AP to ints
        self.AP = AP
        self.AP2int = dict()
        for key, value in enumerate(AP):
            self.AP2int[value] = key

        # Initialize labeling function
        self.state_labels = []

    def _copy_mdp(self, other):
        self.__dict__.update(deepcopy(other.__dict__))

    def new_state(self, reload=False, name=None, label=set()):
        """Create a new labeled state.

        Uses `ConsMDP.new_state` + adds the label. The default label is
        an empty set. Returns the state id.

        Raise `ValueError` if label contains invalid labels
        """
        # TODO: Check for type in label and convert strings to ints
        # Check for invalid AP indices
        for ap in label:
            if ap >= len(self.AP) or ap < 0:
                raise ValueError(f"Given AP index {ap} is invalid. " +
                                 f"Values can be 0-{len(self.AP)-1}.\n" +
                                 f"The set of AP given as label: {label}")

        sid = ConsMDP.new_state(self, reload=reload, name=name)
        self.state_labels.append(label)
        return sid

    def new_states(self, count, labels=None, names=None):
        """Create multiple (`count`) states.

        The length of the lists labels & names (if supplied) must be `count`.

        Return the list of states ids.

        Raise `ValueError` in case of list length mismatch or in case that
        some label contains an invalid AP
        """
        if labels is None:
            labels = [set() for i in count]

        for label in labels:
            for ap in label:
                if ap >= len(self.AP) or ap < 0:
                    raise ValueError(f"Given AP index {ap} is invalid. " +
                                     f"Values can be 0-{len(self.AP) - 1}.\n" +
                                     f"The affected label: {label}\n" +
                                     f"The list of labels: {labels}")
        # TODO Check for type of labels: must be a list

        if count != len(labels):
            raise ValueError("Length of labels must be equal to count.")

        old_length = self.num_states

        sids = ConsMDP.new_states(self, count, names)
        for i in range(count):
            self.state_labels[old_length + i] = labels[i]

        return sids

    def states_with_label(self, label):
        """Return a list of states that carry the given label.

        `label` must be a set of integers that maps to APs.

        Returns an ordered list of integers (states)
        Raise ValueError if some integer is not a valid AP
        """
        # TODO: Check for type in label and convert strings to ints
        # Check for invalid AP indices
        for ap in label:
            if ap >= len(self.AP) or ap < 0:
                raise ValueError(f"Given AP index {ap} is invalid. " +
                                 f"Values can be 0-{len(self.AP) - 1}.\n" +
                                 f"The set of AP given as label: {label}")

        labels = self.state_labels
        states = self.num_states
        return [i for i in range(states) if labels[i] == label]

    def product(self, aut, init_states=None):
        """Product of a labeled CMDP and a deterministic Büchi automaton.

        Parameters
        ==========
         * dba: Spot's object twa_graph representing a deterministic state-based
                Büchi automaton
         * init_states: iterable of ints, the set of initial states of the LCMDP `self`
            The product will be started from these states. If `None`, all states are
            considered initial. At least one state must be declared as initial.

        Raise ValueError when empty init supplied
        Raise ValueError if incorrect type of automaton was given
        Raise ValueError if `dba` uses some AP not used by `self` (LCMDP)
        """
        return product_dba(self, aut, init_states)


