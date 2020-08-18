import spot
import buddy

from consMDP import ConsMDP


def product_dba(lmdp, aut, init_states=None):
    """Product of a labeled CMDP and a deterministic Büchi automaton.

    Parameters
    ==========
     * lcmdp : labeled CMDP (class LCMDP)
     * dba: Spot's object twa_graph representing a deterministic state-based
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
        raise ValueError("The automaton must be state-based deterministic Büchi." +
            "\nYou can get one by calling `aut.postprocess('BA','complete')`")

    # Check if all APs of the dba are used by the MDP
    for ap in aut.ap():
        if ap not in lmdp.AP:
            raise ValueError(f"The automaton uses atomic proposition {ap}" +
                             "not specified in the labeled MDP. Remove it "+
                             "first! Otherwise, determinism is lost.")

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

    result = ConsMDP()
    num_ap = len(lmdp.AP)

    assert num_ap != 0

    # This will store the list of Büchi states
    targets = []
    # This will be our state dictionary
    sdict = {}
    # The list of output states for which we have not yet
    # computed the successors.  Items on this list are triplets
    # of the form `(mdps, auts, p)` where `mdps` is the state
    # number in the mdp, `auts` is the state number in the
    # automaton, and p is the state number in the output mdp.
    todo = []

    # Mapping of AP representation in MDP to repr. in automaton
    ap2bdd_var = {}
    aut_ap = aut.ap()
    for ap_i, ap in enumerate(lmdp.AP):
        if ap in aut_ap:
            ap2bdd_var[ap_i] = aut_ap.index(ap)

    # Given label in mdp, return corresponding BDD
    def get_bdd_for_label(mdp_label):
        cond = buddy.bddtrue
        for ap_i in ap2bdd_var.keys():
            if ap_i in mdp_label:
                cond &= buddy.bdd_ithvar(ap2bdd_var[ap_i])
            else:
                cond -= buddy.bdd_ithvar(ap2bdd_var[ap_i])
        return cond

    # Transform a pair of state numbers (mdps, auts) into a state
    # number in the output mdp, creating a new state if needed.
    # Whenever a new state is created, we can add it to todo.
    def dst(mdps, auts):
        pair = (mdps, auts)
        p = sdict.get(pair)
        if p is None:
            p = result.new_state(name=f"{mdps},{auts}",
                                 reload=lmdp.is_reload(mdps))
            sdict[pair] = p
            todo.append((mdps, auts, p))
            if aut.state_is_accepting(auts):
                targets.append(p)
        return p

    # Get a successor state in automaton based on label
    def get_successor(aut_state, mdp_label):
        for e in aut.out(aut_state):
            mdp_bdd = get_bdd_for_label(mdp_label)
            if mdp_bdd & e.cond != buddy.bddfalse:
                return e.dst

    # Initialization
    # For each state of mdp add a new initial state
    aut_i = aut.get_init_state_number()
    for mdp_s in range(lmdp.num_states):
        label = lmdp.state_labels[mdp_s]
        aut_s = get_successor(aut_i, label)
        dst(mdp_s, aut_s)

    # Build all states and edges in the product
    while todo:
        msrc, asrc, osrc = todo.pop()
        for a in lmdp.actions_for_state(msrc):
            # build new distribution
            odist = {}
            for mdst, prob in a.distr.items():
                adst = get_successor(asrc, lmdp.state_labels[mdst])
                odst = dst(mdst, adst)
                odist[odst] = prob
            result.add_action(osrc, odist, a.label, a.cons)

    return result, targets
