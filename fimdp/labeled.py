from .core import ConsMDP, CounterStrategy, ProductConsMDP, ProductSelector
from .energy_solvers import GoalLeaningES
from .objectives import BUCHI

from copy import deepcopy
from math import inf

import spot
import buddy


class LabeledConsMDP(ConsMDP):
    """Represent consumption MDP with states labeled by sets of Atomic
    Propositions (AP).

    See the docs for ConsMDP for important notes about how to use this
    class in general. We only discuss labeling here.

    The states can now carry both labels with the meaning as name and
    the semantics labels with atomic propositions.

    The set of Atomic propositions that can be used in the labels is
    stored in list `LabeledConsMDP.AP`. The list also establishes a mapping
    from ints to APs. The dict `LabeledConsMDP.AP2int` translates the APs into
    numbers that are actually used for the labels.

    The labeling function is implemented as a list `LabeledConsMDP.state_labels`.
    Complementary, all states with the given set of AP can be obtained
    by`LabeledConsMDP.get_states_with_label()`. The state labels are sets of
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

    def product_with_dba(self, aut, init_states=None):
        """Product of a labeled CMDP and a deterministic Büchi automaton.

        Parameters
        ==========
         * aut: Spot's object twa_graph representing a deterministic state-based
                Büchi automaton
         * init_states: iterable of ints, the set of initial states of the LabeledConsMDP `self`
            The product will be started from these states. If `None`, all states are
            considered initial. At least one state must be declared as initial.


        Returns
        =======
         * (product, targets)
         * product: CMDP object with the product-CMDP
         * targets: target states in the product (accepting states of the Büchi automaton)

        Raise ValueError when empty init supplied
        Raise ValueError if incorrect type of automaton was given
        Raise ValueError if `dba` uses some AP not used by `self` (LabeledConsMDP)
        """
        return product_dba(self, aut, init_states)

    def selector_for_dba(self, aut, init_states=None,
                         cap = inf,
                         SolverClass=GoalLeaningES,
                         keep_product=False):
        """
        Get selector for almost surely satisfaction of specification given as
        deterministic Büchi automaton.

        Build a product of the lCMDP with the automaton and synthesise strategy
        for Büchi objective with targets in states of the product with accepting
        state in the automaton component.

        If `init_states` are given, only consider these states as possible
        initial states. This can save the algorithm from building parts of
        the product that would never be used.

        After the product is analyzed, it is discarded and no longer available,
        unless `keep_product` is `True`. In this case, the product MDP object
        is accessible by `selector.product_mdp`.

        The returned selector is intended to be passed to DBACounterStrategy
        that work directly on top of this LabeledConsMDP.

        Parameters
        ==========

         * aut: Spot's object twa_graph representing a deterministic
             state-based Büchi automaton

         * init_states: iterable of ints, the set of initial states of the
             LabeledConsMDP `self`. The product will be started from these states only.
             If `None`, all states are considered initial. At least one state
             must be declared as initial.
        * SolverClass of energy solvers to be used for analysis of the
            product (GoalLeaningES by default)
        * keep_product: Bool, default False.
            Keep the product MDP associated to the returned selector.

        Returns: `ProductSelector` for Büchi objective given by determinstic
            Büchi automaton `aut`.
        """
        product, targets = self.product_with_dba(aut, init_states)
        solver = SolverClass(product, cap, targets=targets)
        solver.SelectorClass = ProductSelector
        selector: ProductSelector = solver.get_selector(BUCHI)

        if not keep_product:
            del product
            del selector.product_mdp
            del targets

        return selector

    def selector_for_ltl(self, formula, init_states=None,
                         cap = inf,
                         SolverClass=GoalLeaningES,
                         keep_product=False):
        """
        Get selector for almost surely satisfaction of specification given as
        ltl formula.

        Currently, only the recurrence fragment is supported.

        Translate the formula into equivalent deterministic Büchi automaton,
        build a product of the lCMDP with the automaton and synthesise
        strategy for Büchi objective with targets in states of the product
        with accepting state in the automaton component.

        If `init_states` are given, only consider these states as possible
        initial states. This can save the algorithm from building parts of
        the product that would never be used.

        After the product is analyzed, it is discarded and no longer available,
        unless `keep_product` is `True`. In this case, the product MDP object
        is accessible by `selector.product_mdp`.

        The returned selector is intended to be passed to DBACounterStrategy
        that work directly on top of this LabeledConsMDP.

        Parameters
        ==========

         * formula: formula from the recurrence fragment of LTL in format that
            is readable by Spot's Python binding.

         * init_states: iterable of ints, the set of initial states of the
             LabeledConsMDP `self`. The product will be started from these states only.
             If `None`, all states are considered initial. At least one state
             must be declared as initial.
        * SolverClass of energy solvers to be used for analysis of the
            product (GoalLeaningES by default)
        * keep_product: Bool, default False.
            Keep the product MDP associated to the returned selector.

        Returns: `ProductSelector` for Büchi objective given by determinstic
            Büchi automaton `aut`.
        """
        f = spot.formula(formula)
        if f.mp_class() not in "SRPOBG":
            raise ValueError("The formula must be from the recurrence fragment"
                             "of LTL. See https://spot.lrde.epita.fr/hierarchy.html"
                             f"for more details. The formula {f} was given.")
        dba = spot.translate(f, "Buchi", "SBAcc", "deterministic", "complete")
        return self.selector_for_dba(aut=dba, init_states=init_states,
                                     cap=cap, SolverClass=SolverClass,
                                     keep_product=keep_product)


class DBAWrapper:
    """
    Wrapper class around Spot's interface for automaton that answers queries
    for successor in case of deterministic automata.

    AP is a list of names of atomic propositions. The order (and index) of
    the atomic proposition in AP can differ from the order used by the
    automaton. Moreover, the list can contain only a subset of atomic
    propositions of the automaton. It cannot contain superset, as this would
    lead to non-determinism. In queries, atomic propositions should be
    referenced by index in this given list.
    """

    def __init__(self, aut, AP):
        # Check type of automaton
        if not aut.is_deterministic():
            raise ValueError("The automaton is not deterministic.")

        if len(AP) == 0:
            raise ValueError("The list of AP cannot be empty.")

        # Check if all APs of the dba are used by the MDP
        aut_ap = aut.ap()
        for ap in aut_ap:
            if ap not in AP:
                raise ValueError(f"The automaton uses atomic proposition {ap} " +
                                 "not specified in the labeled MDP. Remove it " +
                                 "first! Otherwise, determinism is lost.")

        self.aut = aut
        self.AP = AP

        self.bdd_dict = aut.get_dict()
        self.ap2bdd_var = {}

        # Establish the mapping between AP-indices and BDD variables
        for ap_i, ap in enumerate(AP):
            if ap in aut_ap:
                bddvar_i = aut.get_dict().register_proposition(ap, self)
                self.ap2bdd_var[ap_i] = bddvar_i

    def _bdd_for_label(self, label):
        """Get the BDD for given label (sequence of AP-indices)."""
        cond = buddy.bddtrue
        for ap_i, bdd_var in self.ap2bdd_var.items():
            if ap_i in label:
                cond &= buddy.bdd_ithvar(bdd_var)
            else:
                cond -= buddy.bdd_ithvar(bdd_var)
        return cond

    def __del__(self):
        self.bdd_dict.unregister_all_my_variables(self)

    def edge(self, state, label):
        """
        Get edge from `state` under `label`

        Label is sequence of indices in AP as given by creation of this object.
        """
        for e in self.aut.out(state):
            mdp_bdd = self._bdd_for_label(label)
            if mdp_bdd & e.cond != buddy.bddfalse:
                return e

    def get_init(self):
        return self.aut.get_init_state_number()

    def succ(self, state, label):
        """
        Get successor from `state` under `label` given as indices to self.AP.
        """
        return self.edge(state, label).dst


class DBACounterStategy(CounterStrategy):
    """
    Strategy for labeled ConsMDPs `mdp` with 2 components of memory:
     1. counter to maintain energy level of the play, and
     2. deterministic Büchi automaton that runs on the labels produced by the
        play.

    It uses ProductSelector built for the corresponding product mdp × dba
    for selecting the next actions on the original mdp.

    At initialization, if both `init_state` and `init_aut_state` are given,
    the play starts in configuration `(init_state, init_aut_state)`. If only
    `init_state` is given, the play starts at `(init_state, aut_state)` where
    `aut_state=δ(qi, label(init_state))` is the successor of the initial state
    `qi` of `aut` under the label of `init_state`. If only `init_aut_state` is
    given, the initial state needs to be given by `update(outcome)` and the
    automaton state will be updated based on `outcome` to the corresponding
    successor `aut_init_state`. If neither is given, the previous applies with
    `aut_init_state=qi`, which means that the automaton starts from its initial
    state.
    """
    def __init__(self, mdp: LabeledConsMDP, aut,
                 selector: ProductSelector,
                 capacity: int, init_energy: int, init_state=None,
                 *args, **kwargs):
        # Check the type of mdp
        if not isinstance(mdp, LabeledConsMDP):
            raise ValueError("Argument `mdp` must be a labeled consumption "
                             f"MDP (LabeledConsMDP). It is of type {type(mdp)}")

        # Check the type of automaton
        if not (aut.is_sba() and aut.is_deterministic()):
            raise ValueError(
                "The automaton must be state-based deterministic Büchi."
                "If the property is DBA-realizable, get one by calling: "
                "`aut.postprocess('BA','complete','deterministic')`")

        # Check if all APs of the dba are used by the MDP
        for ap in aut.ap():
            if ap not in mdp.AP:
                raise ValueError(
                    f"The automaton uses atomic proposition {ap}" +
                    "not specified in the labeled MDP. Remove it " +
                    "first! Otherwise, determinism is lost.")

        self.aut = DBAWrapper(aut, mdp.AP)
        super().__init__(mdp, selector, capacity,
                         init_energy, init_state,
                         *args, **kwargs)
        self.mdp = mdp

    def _next_action(self):
        mdp_s = self._current_state
        aut_s = self.aut_state
        energy = self.energy
        return self.selector.select_action(mdp_s, aut_s, energy)

    def _update(self, outcome):
        super()._update(outcome)
        label = self.mdp.state_labels[outcome]
        self.aut_state = self.aut.succ(self.aut_state, label)

    def _reset(self, init_energy=None, init_aut_state=None, *args, **kwargs):
        super()._reset(init_energy)
        if init_aut_state is not None and self._current_state is not None:
            self.aut_state = init_aut_state
        else:
            if init_aut_state is None:
                init_aut_state = self.aut.get_init()
            if self._current_state is not None:
                label = self.mdp.state_labels[self._current_state]
                self.aut_state = self.aut.succ(init_aut_state, label)
            else:
                self.aut_state = init_aut_state


def product_dba(lmdp, aut, init_states=None):
    """Product of a labeled CMDP and a deterministic Büchi automaton.

    Parameters
    ==========
     * lmdp : labeled CMDP (class LabeledConsMDP)
     * aut: Spot's object twa_graph representing a deterministic state-based
            Büchi automaton
     * init_states: iterable of ints, the set of initial states of the lcmdp
        The product will be started from these states. If `None`, all states are
        considered initial. At least one state must be declared as initial.

    Returns
    =======
     * (product, targets)
     * product: CMDP object with the product-CMDP
     * targets: target states in the product (accepting states of the Büchi automaton)

    Raise ValueError when empty init supplied
    Raise ValueError if incorrect type of automaton was given
    Raise ValueError if `dba` uses some AP not used by `lcmdp`
    """
    # Check the type of automaton
    if not aut.is_sba():
        raise ValueError("The automaton must be state-based deterministic"
                         "Büchi. You can get one by calling `aut.postprocess("
                         "'BA','complete')`")

    # All states are initial unless specified otherwise
    if init_states is None:
        init_states = range(lmdp.num_states)

    # Check for emptiness of init
    if len(init_states) == 0:
        raise ValueError("The collection of initial states must not be empty")

    # complete DBA if needed
    # TODO: log the changed automaton?
    if not spot.is_complete(aut):
        aut = aut.postprocess("BA", "complete")

    dba = DBAWrapper(aut, lmdp.AP)
    result = ProductConsMDP(lmdp, aut)

    # Output states for which we have not yet computed the successors and
    # Büchi states
    todo, targets = [], []

    # Transform a pair of state numbers (mdps, auts) into a state
    # number in the output mdp, creating a new state if needed.
    # Whenever a new state is created, we can add it to todo.
    def get_or_create(mdps, auts):
        p = result.get_state(mdps, auts)
        if p is None:
            p = result.new_state(mdps, auts,
                                 reload=lmdp.is_reload(mdps))
            todo.append(p)
            if aut.state_is_accepting(auts):
                targets.append(p)
        return p

    # Initialization
    # For each state of mdp in init_states, add a new initial state
    aut_i = aut.get_init_state_number()
    for mdp_s in init_states:
        label = lmdp.state_labels[mdp_s]
        aut_s = dba.succ(aut_i, label)
        get_or_create(mdp_s, aut_s)

    # Build all states and edges in the product
    while todo:
        osrc = todo.pop()
        msrc, asrc = result.components[osrc]
        for a in lmdp.actions_for_state(msrc):
            # build new distribution
            odist = {}
            for mdst, prob in a.distr.items():
                label = lmdp.state_labels[mdst]
                aedge = dba.edge(asrc, label)
                adst = aedge.dst
                odst = get_or_create(mdst, adst)
                odist[odst] = prob
            result.add_action(osrc, odist, a.label, a.cons,
                              orig_action=a, other_action=aedge)

    return result, targets
