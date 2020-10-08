# ChangeLog for [FiMDP](https://github.com/xblahoud/FiMDP) (Fuel in MDP) project

## [Unpublished]

### Added
 * Solvers that use heuristics for strategies usable in control. This is implemented in class
   `GoalLeaningES` of the `energy_solver.py` module. See [tut/Solvers](tut/Solvers.ipynb)
   notebook for more details. Use [nbviewer] for the rendered notebook if you don't want
   to run the notebook locally; it renders the animations correctly.
 * Support for full-featured strategies that resolve the next action to play based on the history. See `Strategy`
   for the interface. See [tut/Strategies](tut/Strategies.ipynb) for more details.
     - `CounterStrategy` implements strategies with a limited memory. The class only
     maintains the energy level of the play and can use it for the selection of next
     actions. The class only implements the memory and relies on `selector` objects
     to choose the next action. Any object implementing `select_action(state, energy)`
     can be used as selector.
     - `CounterSelector` is an enriched variant of what was called "strategy" in
     versions up to 1.2. This is the class intended to be used by the
     `CounterStrategy` instances.
     - `SelectionRule` is a helper class that stores the selection rules for one
     state. It is basically a `dict` enriched with `select_action` (and `update`)
     function. The keys in this `dict` are lower bounds of intervals that are
     mapped to the corresponding values. `select_action` takes care of the
     translation of lower bounds to intervals.
 * Integration with Stormpy for reading PRISM and Storm models into FiMDP and for
   translation of FiMDP models into equivalent models in Stormpy. See 
   [tut/Storm_and_prism](tut/StormAndPrism.ipynb) for more details.
 * Ability to reason about Consumption MDPs with state labeled by sets of atomic propositions. 
   This is implemented in the module `labeled.py`. The labeled ConsMDPs can be checked against
   specifications given by deterministic DBAs or the recurrence fragment of LTL. This requires
   [Spot] to be installed. See [tut/Labeled](tut/Labeled.ipynb) for more details.
 * Binary search for detection of minimal capacity needed for a task
   (function `mincap_solvers.bin_search`).
 
### Changed

#### Backward incompatible changes
 * The class `ConsMDP` and its helper classes (`ActionData` and iterators) are moved
  from `consMDP.py` module to `core.py`.
 * The update function of energy solvers now stores pointer to the whole ActionData object instead of
   just label. Add `.label` to every access to actions stored in the current representations
   of strategies.

#### Backward compatible changes
 * `EnergySolvers.get_strategy` returns `CounterSelector` objects instead of `list` of `dict`s
 * `ActionData.__repr__` now prints full information about the action (source state, consumption, label, and successor distribution).

## [1.0.2]

### Added
 * data structures for *consumption Markov Decision Processes (CMDP)*
 * Solvers for strategy synthesis (and solving underlying decision problems) for Survival, Positive reachability 
 (of given target set $`T`$), almost-sure reachability of $`T`$, and almsot-sure Büchi objective on $`T`$
 * Algorithm for explicit representation of energy + MEC decomposition of this explicit MDP
 * example notebooks

[Unpublished]: https://github.com/xblahoud/FiMDP/compare/v1.0.2..HEAD
[1.0.2]: https://github.com/xblahoud/FiMDP/tree/v1.0.2

[nbviewer]: https://nbviewer.jupyter.org/