from collections import defaultdict

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


# Decompose MDP into MECs. Ignores consumption.
#
# The algorithm uses decomposition of directed graph using
# Tarjan's algorithm (single DFS). The implementation of this
# the Tarjan's algo is inspired from:
# https://www.geeksforgeeks.org/tarjan-algorithm-find-strongly-connected-components/
def get_MECs(mdp):
    """Given an MDP (not necessarly consMDP), compute its
    maximal-end-components decomposition.

    Returns list of mecs (lists).
    """
    g = _mdp2graph(mdp)
    mecs = []
    removed = set()
    # detect states of bSCCs
    while len(g.graph) > 0:
        to_remove = set()
        sccs = g.SCC()
        for scc_i, scc in enumerate(sccs):
            if g.check_bscc(scc) and not g.check_trivial(scc):
                to_remove.update(scc)
                mecs.append(scc)

        attr = _prob_attractor(mdp, removed.union(to_remove))
        g.remove_vertices(attr)
        removed.update(attr)

    return mecs


class _Graph:
    '''
    Represent graphs using adjacency list representation
    '''
    def __init__(self):
        # default dictionary to store graph
        self.graph = defaultdict(list)

        self.Time = 0

        self.sccs = []

    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)

    def _SCCUtil(self, u, low, disc, stackMember, st):
        '''A recursive function that find finds strongly connected
            components using DFS traversal
            u --> The vertex to be visited next
            disc[] --> Stores discovery times of visited vertices
            low[] -- >> earliest visited vertex (the vertex with minimum
                        discovery time) that can be reached from subtree
                        rooted with current vertex
             st -- >> To store all the connected ancestors (could be part
                   of SCC)
             stackMember[] --> bit/index array for faster check whether
                          a node is in stack
        '''

        # Initialize discovery time and low value
        disc[u] = self.Time
        low[u] = self.Time
        self.Time += 1
        stackMember[u] = True
        st.append(u)

        # Go through all vertices adjacent to this
        for v in self.graph[u]:

            # If v is not visited yet, then recur for it
            if disc[v] == -1:

                self._SCCUtil(v, low, disc, stackMember, st)

                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                # Case 1 (per above discussion on Disc and Low value)
                low[u] = min(low[u], low[v])

            elif stackMember[v]:

                # Update low value of 'u' only if 'v' is still in stack
                # (i.e. it's a back edge, not cross edge).
                low[u] = min(low[u], disc[v])

                # head node found, pop the stack and print an SCC
        w = -1  # To store stack extracted vertices
        if low[u] == disc[u]:
            scc = []
            while w != u:
                w = st.pop()
                scc.append(w)
                stackMember[w] = False

            self.sccs.append(scc)

    def SCC(self):
        """Find strongly connected components using Tarjan's algorithm.

        Take `self.removed` into account: skip edges between removed nodes.

        Uses self._SCCUtil.
        """

        # Mark all the vertices as not visited
        # and Initialize parent and visited,
        # and ap(articulation point) arrays
        disc = {u : -1 for u in self.graph.keys()}
        low = {u : -1 for u in self.graph.keys()}
        stackMember = {False : -1 for u in self.graph.keys()}
        st = []
        self.sccs = []

        # Call the recursive helper function
        # to find articulation points
        # in DFS tree rooted with vertex 'i'
        for u in self.graph:
            if disc[u] == -1:
                self._SCCUtil(u, low, disc, stackMember, st)

        return self.sccs

    def remove_vertices(self, to_remove):
        for u in to_remove:
            self.graph.pop(u, None)
        for u, succs in self.graph.items():
            self.graph[u] = [v for v in succs if v not in to_remove]

    def check_bscc(self, scc):
        """Check if scc is botton and non-trivial -- has cycle"""
        for s in scc:
            for t in self.graph[s]:
                if t not in scc:
                    return False
        return True

    def check_trivial(self, scc):
        for s in scc:
            for t in self.graph[s]:
                if t in scc:
                    return False
        return True


def _prob_attractor(mdp, attr):
    """ Compute a set of states from which I cannot avoid
    states from SCCs pointed by `scc_ind`.
    scc_indices are pointers to graph_sccs.

    We exploit that graph_sccs are in reverse topological
    order.
    """
    repeat = True
    while repeat:
        repeat = False
        for s in range(mdp.num_states):
            if s in attr:
                continue

            safe = False
            for a in mdp.actions_for_state(s):
                if len(a.get_succs().intersection(attr)) == 0:
                    safe = True

            if not safe:
                attr.add(s)
                repeat = True

    return attr


def _mdp2graph(mdp):
    """Convert mdp to graph representation for the Tarjan algo"""
    ns = mdp.num_states # store the number of states
    g = _Graph()

    for s in range(ns):
        for t in mdp.state_succs(s):
            g.addEdge(s,t)

    return g
