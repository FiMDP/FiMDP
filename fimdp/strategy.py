"""
Module that implements counter-strategies.

The main ingredient of a counter strategy is *counter selector*. A counter
selector is a mapping from states to *selection rules*. A selection rule
selects actions based on given energy level.

The class `Strategy` implements the basic interface for strategies, but it
neither updates any memory nor picks actions. Its subclasses should override
the function `._next_action()` and (when using memory) also `._update(outcome)`.

See our [CAV paper] for details.

## Interface for strategies

A `strategy` should offer `strategy.next_action()` that picks an action based
on history, and the function `strategy.update_state(outcome)` which tells the
strategy that the last action was resolved to the state outcome — which
becomes the new current state. Each call to `next_action()` should be
followed by a call to `update_state` and vice versa. Both functions raise
`WrongCallOrderError` if the calls do not alternate.

To simplify code, `strategy.next_action(outcome)` is a shorthand for

>>> strategy.update_state(outcome)
>>> strategy.next_action()

The function `update_state(outcome)` raises a `ValueError` if `outcome` is
not a valid successor for the last action returned by `next_action()`. Based
on the `outcome`, the strategy can update its memory.

[CAV paper]: https://link.springer.com/chapter/10.1007/978-3-030-53291-8_22
"""


class Strategy:
    """
    Abstract class that implements the interface for strategies (see the
    docstring for the `strategy.py` module). It handles the checks for
    outcomes and alternation of calls to `.next_action` and `.update_state`.

    Calls to `.next_action()` and `.update_state(outcome)` should alternate
    unless `next_action(outcome)` are used exclusively.
    """

    def __init__(self, mdp, init_state=None, *args, **kwargs):
        self.mdp = mdp
        self.reset(init_state, *args, **kwargs)

    def next_action(self, outcome=None):
        """
        Pick the next action to play

        :param outcome: sid (state id) or `None` (default `None`)
            `outcome` must be a successor of the action picked by the last call
            to `.next_action()`. If defined, update the current state to
            `outcome`.
        :return: action to play
        """
        if outcome is not None:
            self.update_state(outcome)
        if self._current_action is not None:
            raise WrongCallOrderError("The outcome of the last action is not "
                                      "known. Supply it using the `outcome` "
                                      "parameter or using the function"
                                      "`strategy.update_state(outcome)`.")
        self._current_action = self._next_action()
        return self._current_action

    def update_state(self, outcome):
        """
        Tells the strategy that the last action picked by `next_action` was
        resolved to `outcome`.

        :param outcome: sid (state id)
            `outcome` must be a successor of the action picked by the last call
            to `.next_action()`.
        """
        # Only run checks if this is not the first call to update_state
        # The first call basically sets the initial state
        if self._current_state is not None:
            if self._current_action is None:
                raise WrongCallOrderError("`strategy.update_state()` must be called"
                                          " after `strategy.next_action()`.")
            if outcome not in self._current_action.distr:
                raise ValueError(f"The outcome {outcome} is not a valid successor "
                                 f"for the last action picked by this strategy. "
                                 f"The list of possible outcomes is "
                                 f"{list(self._current_action.distr.keys())}.")
        self._update(outcome)
        self._current_action = None
        self._current_state = outcome

    def reset(self, init_state=None, *args, **kwargs):
        self._current_action = None
        self._current_state = init_state

    def _next_action(self):
        raise NotImplementedError()

    def _update(self, outcome):
        pass


class CounterStrategy(Strategy):
    """
    Counter strategy tracks energy consumption in memory and chooses next
    action based on the current state and the current energy level.

    This class implements the memory and its updates. The selection itself is
    delegated to `selector`. The attributes `capacity` and `init_energy` are
    needed to track the energy level correctly.

    The implementation is suited to use CounterSelector as `selector`, but can
    take anything that implements `select_action(state, energy)`.
    """

    def __init__(self, mdp, selector, capacity, init_energy, init_state=None):
        super(CounterStrategy, self).__init__(mdp,
                                              init_state,
                                              init_energy=init_energy)
        self.capacity = capacity
        self.selector = selector

    def _next_action(self):
        return self.selector.select_action(self._current_state, self.energy)

    def _update(self, outcome):
        """
        Unless called to set the initial state, update energy by substracting
        the consumption of the `_current_action`. If `_current_state` is a reload
        state, recharge to full capacity before the substraction.
        """
        if self.mdp.is_reload(self._current_state):
            self.energy = self.capacity

        # Don't update energy on the first call
        if self._current_action is not None:
            self.energy -= self._current_action.cons

    def reset(self, init_state=None, init_energy=None, *args, **kwargs):
        """Reset the strategy to a new init_state with init_energy.

        Throws away the previous history.

        *args and **kwargs are ignored.
        """
        super(CounterStrategy, self).reset(init_state)
        if init_energy is not None:
            self.energy = init_energy


class CounterSelector(list):
    """
    CounterSelector can select actions based on current state and energy.

    Counter selector is a list of SelectionRules extended by:
     * pointer to the corresponding mdp
     * and 2 functions for updating and accessing actions to be taken:
        - update(state, energy_level, action)
        - select_action(state, energy)
    """

    def __init__(self, mdp, values=None):
        """
        ConsMDP `mdp` is where the selector picks actions.
        `values` can be a list of dicts with the values for the selector.
        """
        self.mdp = mdp
        self._init_selector(values)

    def _init_selector(self, values):
        num_states = self.mdp.num_states
        if values is None:
            for s in range(num_states):
                self.append(SelectionRule())
        else:
            assert len(values) == num_states
            assert len(self) == 0
            for rule in values:
                self.append(SelectionRule(rule))

    def update(self, state, energy_level, action):
        """
        Update the action for given `state` and `energy_level` to `action`.

        `energy_level` is an lower bound of an interval for which `action`
        will be selected by `select_action`.
        """
        if action not in self.mdp.actions_for_state(state):
            raise ValueError(f"The action {action} is not valid for the state "
                             f"{state}.")
        self[state][energy_level] = action

    def select_action(self, state, energy):
        """
        Return action selected for `state` and `energy`
        """
        return self[state].select_action(energy)

    def __copy__(self):
        """Return a shallow copy of the CounterSelector"""
        res = CounterSelector(self.mdp)
        for rule in self:
            res.append(rule)
        return res

    def __deepcopy__(self, memodict={}):
        """Return a deep copy of the CounterSelector"""
        return CounterSelector(self.mdp, values=self)



class SelectionRule(dict):
    """
    Selection rule is a partial function: ℕ → Actions.

    Intuitively, a selection according to rule φ selects the action
    that corresponds to the largest value from dom(φ) that  is  not
    larger than the given energy level.

    For dom(φ) = n₁ < n₂ < ... < n_k and energy level e the selection
    returns φ(n_i) where i is largest integer such that n_i <= e.
    """

    def select_action(self, energy):
        """Select action for given energy level.

        :param energy: energy level
        :return: action selected by the rule for `energy`
        :raise: `NoFeasibleActionError` if no action can be selected for the
                given `energy`
        """
        candidate_interval, candidate_action = -1, None
        for lower_bound, action in self.items():
            if energy >= lower_bound > candidate_interval:
                candidate_interval, candidate_action = lower_bound, action

        if candidate_action is None:
            raise NoFeasibleActionError(f"No action is feasible for energy "
                                        f"level {energy}")
        return candidate_action

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return SelectionRule(self)

    def __str__(self):
        """
        Print each rule as a line iof the form `interval: action.label`.
        """
        keys = sorted(self.keys())
        records = []
        for i, k in enumerate(keys):
            # Get the bounds of the intervals
            lower = k
            upper = keys[i+1] - 1 if i < len(keys) - 1 else None

            # Print l+ for the unbounded interval
            if upper is None:
                records.append(f"{lower}+: {self[k].label}")
            else:
                records.append(f"{lower} — {upper}: {self[k].label}")

        records_str = (',\n  ').join(records)
        return "{\n  " + records_str + "\n}"


class NoFeasibleActionError(Exception):
    pass


class WrongCallOrderError(Exception):
    pass
