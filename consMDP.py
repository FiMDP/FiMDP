from dot import consMDP2dot, dot_to_svg
from IPython.display import SVG
import safety

def is_distribution(d):
    probs = d.values()
    return sum(probs) == 1

class ConsMDP:
    """Represent Markov Decission Process with consumption on actions.

    The data describing the MDP are stored mainly in two vectors:
     - `succ`
     - `actions`
    States are represented by integers and `succ[i]` stores the index to
    the list `actions` where the data for `i` start. Thus `actions[succ[i]]`
    hold the first action of `i`. 

    States can be labeled using the list `labels`. Reload states are stored
    in the set `reload_states`
    """

    def __init__(self):
        self.name = None

        self.succ = []
        self.actions = [0]
        
        self.state_labels = []
        self.reloads = []
        
        self.num_states = 0
        self.minInitCons = None
        
    def new_state(self, reload=False, label=None):
        # check for existing label
        if label is not None:
            for i,l in enumerate(self.state_labels):
                if l == label:
                    raise ValueError("State with label \"{}\" already exists (id={})".
                                    format(label, i))
        
        sid = self.num_states
        
        self.succ.append(0)
        self.reloads.append(reload)
        self.state_labels.append(label)
        self.num_states+=1
        return sid
    
    def new_states(self, count, labels = None):
        #TODO add reload list
        """Create multiple (`count`) states.

        The list lables must have length `count` if supplied. These will be
        the labels for the states.

        Return the list of states ids.
        """
        if labels is not None:
            if count != len(labels):
                raise ValueError("Length of labels must be equal to count.")

        start = self.num_states
        for i in range(count):
            l = None if labels is None else labels[i]
            self.new_state(l)
        return range(start, start+count)

    def set_reload(self, sid, reload=True):
        #TODO extend to lists of states
        """Set reload status of state `sid`.

        Set to True by default."""
        self.reloads[sid] = reload

    def unset_reload(self, sid):
        """Set the state `sid` *not* to be a reload state.

        Equivalent to
        ``
        set(sid, False)
        ``
        """
        self.reloads[sid] = False

    def is_reload(self, sid):
        """Return the reload status of state `sid`."""
        return self.reloads[sid]

    def add_action(self, src, distribution, label, consumption = 0):
        """Add action to consMDP.
        
        Returns: index of the new action in the `actions` list.
        Raises: 
          * `ValueError` if attempt to use non-existent state
          * `ValueError` if src-label->... exists already. 
        """
        # Check that src exists
        if src >= self.num_states:
            raise ValueError(f"State {src} given as src does not exists.")
        
        # Check that all destinations exist
        for k in distribution.keys():
            if k >= self.num_states:
                raise ValueError(f"State {k} does not exists.")
                
        # check for determinism on action labels
        # raise ValueError if nondeterminsm would occur
        for a in self.actions_for_state(src):
            if a.label == label:
                raise ValueError(
                    "State {} already has an action with label {}".format(src, label))
        aid = len(self.actions)
        
        # Update the lists accordingly:
        #  * `next_succ` of last action for src if any, or
        #  * `succ[src]`  if it's first action for src
        a = self.actions_for_state(src).get_last()
        if a is None:
            self.succ[src] = aid
        else:
            a.next_succ = aid
        
        adata = ActionData(src, consumption, distribution, label, 0)
        self.actions.append(adata)
        return aid
    
    def remove_action(self, aid):
        """Remove action based on its id."""
        # TODO add checks
        if aid <= 0 or aid >= len(self.actions):
            raise ValueError(f"The supplied aid {aid} is not a valid action id.")
        if self.actions[aid].next_succ == aid:
            raise ValueError(f"Action aid ({aid}) was already deleted.")

        src = self.actions[aid].src
        it = self.out_iteraser(src)
        next(it)
        while it.curr != aid:
            next(it)
        it.erase()

    def actions_for_state(self, s):
        """Return iterator of actions available for state `s`."""
        it = Succ_iter(self.actions, self.succ[s])
        return it

    def out_iteraser(self, s):
        """Return iterator of actions available for state `s`."""
        it = Succ_iteraser(self, s)
        return it

    def compute_minInitCons(self, recompute=False):
        MI = safety.minInitCons(self)
        self.minInitCons = MI
        MI.get_values(recompute)

    def get_dot(self, options=""):
        dwriter = consMDP2dot(self, options)
        return dwriter.get_dot()

    def show(self, options=""):
        return SVG(dot_to_svg(self.get_dot(options)))
        
    def _repr_dot_(self):
        return self.get_dot()

    def _repr_svg_(self):
        return dot_to_svg(self._repr_dot_())
        
        
class ActionData:
       
    
    def __init__(self, src, cons, distr, label, next_succ):
        if not is_distribution(distr):
            raise AttributeError("Supplied dict is not a distribution." +
                                 " The probabilities are: {}".format
                                 (list (distr.values()) ) )
        self.src = src
        self.cons = cons
        self.distr = distr
        self.label = label
        self.next_succ = next_succ
        
    def get_all_succ(self):
        return list(distr.keys())
    

class Succ_iter:
    """Iterate over linked list nested in a given List.
    
    Expect that the items stored in `l` contain field `next_succ` which
    contain integers that are indices in `l` where new successor can be
    found.
    
    Assumptions
    ===========
     * List `l` is indexed from 1
     * `next_succ = 0` means last item of the linked list (`succ`)
     
    ..attribute: l
    
        List of items containing `next_succ` fields. Indexed from 1
        
    ..attribute: i
        
        Index in `l` of the first element of the nested list.
    
    """
    def __init__(self, l, i):
        # TODO check for types
        self.l = l
        self.next = i

    def __iter__(self):
        return self

    def __next__(self):
        if self.next == 0:
            raise StopIteration()
        if self.next >= len(self.l):
            raise IndexError("{} ".format(self.l)+f"{self.next}")
        else:
            item = self.l[self.next]
            self.next = item.next_succ
            return item
        
    def is_empty(self):
        return self.next == 0
    
    def get_last(self):
        a = None
        while not self.is_empty():
            a = self.__next__()
        return a  
    
    def __len__(self):
        c = 0
        while not self.is_empty():
            a = self.__next__()
            c += 1
        return c

class Succ_iteraser(Succ_iter):
    """Iterate over outgoing edges of `s` and allow erasing edges.

    Expects an consMDP `mdp` and state index `s`. The function erase
    erases the current action and moves to the next one for `s`.
    """

    def __init__(self, mdp, s):
        super(Succ_iteraser,self).__init__(mdp.actions, mdp.succ[s])
        self.curr = None
        self.prev = None
        self.s    = s
        self.succ = mdp.succ

    def __next__(self):
        self.prev = self.curr
        self.curr = self.next
        return super(Succ_iteraser,self).__next__()

    def erase(self):
        if self.curr is None:
            raise ValueError("Can't erase before moved to 1st edge. Call self.__next__() first")
        self.l[self.curr].next_succ = self.curr
        if self.prev is None:
            self.succ[self.s] = self.next
        else:
            self.l[self.prev].next_succ = self.next
