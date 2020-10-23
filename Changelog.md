# ChangeLog for [FiMDP](https://github.com/xblahoud/FiMDP) (Fuel in MDP) project

## [Unpublished]

## [2.0.0]

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
 * `fimdp.setup()` configures FiMDP to create nicer pictures of ConsMDPs.
 * Solvers can now be visualized. Legend for the semantics of the minimal levels can be 
   requested by calling `solver.show(.l)`
 * Show now takes `<N` option where the integer `N` marks the maximal number of states that
   should be drawn. It can be also specified by `max_states=N`.
 * `ConsMDP.show` takes `targets` argument which enables to highlight the given
   set of targets. Alternatively, targets can be specified using the option
   string `".T{t₁,t₂,...}"`. This cannot be used for solvers.
 
### Changed

The package underwent a massive refactoring. There is a completely new interface for
energy solvers, part of the ConsMDP interface was removed (in favor of solvers), and
most of the codes was moved to new (or renamed) modules. The changes are listed below
and split into backward-incompatible and -compatible. 

#### Backward incompatible changes
 * `ConsMDP` class does no longer have functions `get_buchi` and similar. Instead,
   solvers must be used explicitly. Moreover, they have no solver associated anymore
   and when visualized, they never show minimal levels for objectives (visualize solver
   instead). 
   See [tut/Basics][Basics] for more details.
 * Solvers have new interface. See the corresponding 
   [issue #29](https://github.com/xblahoud/FiMDP/issues/29) or the [Basics] notebook
   for more details.
 * **moved between modules:**
   - The class `ConsMDP` and its helper classes (`ActionData` and iterators) are moved
     from `consMDP.py` module to `core.py`.
   - Code regarding explicit encoding of energy to state-space was moved to `explicit.py`
   - Fixpoints-related code was moved to `energy_solvers.py`
   - Objectives definitions (BUCHI, etc.) moved to `objectives.py`
 * `energy_solver.py` renamed to `energy_solvers.py`
 * The update function of energy solvers now stores pointer to the whole ActionData object instead of
   just label. Add `.label` to every access to actions stored in the current representations
   of strategies.

#### Backward compatible changes
 * `EnergySolvers.get_strategy` returns `CounterSelector` objects instead of `list` of `dict`s
 * `ActionData.__repr__` now prints full information about the action (source state, consumption, label, and successor distribution).
 * Visualization uses various shapes where appropriate.

## [1.0.2]

### Added
 * data structures for *consumption Markov Decision Processes (CMDP)*
 * Solvers for strategy synthesis (and solving underlying decision problems) for Survival, Positive reachability 
 (of given target set $`T`$), almost-sure reachability of $`T`$, and almsot-sure Büchi objective on $`T`$
 * Algorithm for explicit representation of energy + MEC decomposition of this explicit MDP
 * example notebooks

[Unpublished]: https://github.com/FiMDP/FiMDP/compare/v2.0.0..HEAD
[2.0.0]: https://github.com/FiMDP/FiMDP/compare/v2.0.0..v1.0.2
[1.0.2]: https://github.com/FiMDP/FiMDP/tree/v1.0.2

[Basics]: tut/Basics.ipynb

[nbviewer]: https://nbviewer.jupyter.org/
[Spot]: https://spot.lrde.epita.fr/
