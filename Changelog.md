# ChangeLog for [FiMDP](https://github.com/xblahoud/FiMDP) (Fuel in MDP) project

## [Unpublished]

### Added
 * Solvers that use heuristics for strategies usable in control. This is implemented in class
   `GoalLeaningES` of the `energy_solver.py` module. See [tut/StrategyTypes](tut/StrategyTypes.ipynb)
   notebook for more details. Use nbviewer.jupyter.org/ for the rendered notebook if you don't want
   to run the notebook locally; it renders the animations correctly.
 * Binary search for detection of minimal capacity needed for a task (function `mincap.bin_search`).
 
### Changed
 * BW. INCOMPATIBLE: The update function of energy solvers now stores pointer to the whole ActionData object instead of 
   just label. Add `.label` to every access to actions stored in the current representations
   of strategies.

## [1.0.2]

### Added
 * data structures for *consumption Markov Decision Processes (CMDP)*
 * Solvers for strategy synthesis (and solving underlying decision problems) for Survival, Positive reachability 
 (of given target set $`T`$), almost-sure reachability of $`T`$, and almsot-sure Büchi objective on $`T`$
 * Algorithm for explicit representation of energy + MEC decomposition of this explicit MDP
 * example notebooks

[Unpublished]: https://github.com/xblahoud/FiMDP/compare/v1.0.2..HEAD
[1.0.2]: https://github.com/xblahoud/FiMDP/tree/v1.0.2