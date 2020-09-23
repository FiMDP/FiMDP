from .core import ProductConsMDP


def product_energy(cmdp, capacity, targets=[]):
    """Explicit encoding of energy into state-space

    The state-space of the newly created MDP consists of tuples `(s, e)`,
    where `s` is the state of the input CMDP and `e` is the energy level.
    For a tuple-state `(s,e)` and an action $a$ with consumption (in the
    input CMDP) `c`, all successors of the action `a` in the new MDP are
    of the form `(s', e-c)` for non-reload states and
    `(r, capacity)` for reload states.
    """
    result = ProductConsMDP(cmdp, capacity)
    # The list of output states for which we have not yet
    # computed the successors.  Items on this list are triplets
    # of the form `(s, e, p)` where `s` is the state
    # number in the mdp, `e` is the energy level, and p
    # is the state number in the output mdp.
    todo = []
    otargets = []
    sink_created = False

    # Transform a pair of state numbers (s, e) into a state
    # number in the output mdp, creating a new state if needed.
    # Whenever a new state is created, we can add it to todo.
    def dst(s, e):
        p = result.get_state(s, e)
        if p is None:
            p = result.new_state(s, e,
                                 reload=cmdp.is_reload(s))
            if s in targets and e >= 0:
                otargets.append(p)
            todo.append((s, e, p))
        return p

    # Initialization
    # For each state of mdp add a new initial state
    for s in range(cmdp.num_states):
        dst(s, capacity)

    # Build all states and edges in the product
    while todo:
        s, e, p = todo.pop()
        for a in cmdp.actions_for_state(s):
            # negative goes to sink
            if e - a.cons < 0:
                if not sink_created:
                    sink = result.new_state(-1, "-∞", name="sink,-∞")
                    result.add_action(sink, {sink: 1}, "σ", 1, None)
                    sink_created = True
                result.add_action(p, {sink: 1}, a.label, a.cons, a)
                continue
            # build new distribution
            odist = {}
            for succ, prob in a.distr.items():
                new_e = capacity if cmdp.is_reload(succ) else e - a.cons
                out_succ = dst(succ, new_e)
                odist[out_succ] = prob
            result.add_action(p, odist, a.label, a.cons, a)

    return result, otargets
