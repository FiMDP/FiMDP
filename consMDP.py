from dot import consMDP2dot, dot_to_svg

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
        self.reload_states = set()
        self.target_states = set()
        
        self.states_num = 0
        
    def new_state(self, label=None):
        # check for existing label
        if label is not None:
            for i,l in enumerate(self.state_labels):
                if l == label:
                    raise ValueError("State with label \"{}\" already exists (id={})".
                                    format(label, i))
        
        sid = self.states_num
        
        self.succ.append(0)
        self.state_labels.append(label)
        self.states_num+=1
        return sid
    
    def add_action(self, src, distribution, label, consumption = 0):
        """Add action to consMDP.
        
        Returns: index of the new action in the `actions` list.
        Raises: 
          * `ValueError` if attempt to use non-existent state
          * `ValueError` if src-label->... exists already. 
        """
        # Check that src exists
        if src >= self.states_num:
            raise ValueError(f"State {src} given as src does not exists.")
        
        # Check that all destinations exist
        for k in distribution.keys():
            if k >= self.states_num:
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
    
    def actions_for_state(self, s):
        """Return iterator of actions available for state `s`."""
        it = Succ_iter(self.actions, self.succ[s])
        return it

    def _repr_dot_(self):
        dwriter = consMDP2dot(self)
        return dwriter.get_dot()

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
        self.i = i

    def __iter__(self):
        return self

    def __next__(self):
        if self.i == 0:
            raise StopIteration()
        if self.i >= len(self.l):
            raise IndexError("{} ".format(self.l)+f"{self.i}")
        else:
            item = self.l[self.i]
            self.i = item.next_succ
            return item
        
    def is_empty(self):
        return self.i == 0
    
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