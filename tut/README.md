# Tutorials for [FiMDP]

For rendered versions of these notebooks, visit them on [nbviewer] on this [link](https://nbviewer.jupyter.org/github/FiMDP/FiMDP/tree/master/tut/). You need Graphviz installed in your PATH to run the notebooks locally.

[Basics](Basics.ipynb) covers the basic use cases of [FiMDP]: building a ConsMDP, using the basic energy solver for qualitative analysis and controller synthesis over ConsMDP, and finally using and simulating strategies.

[Explicit energy](ExplicitEnergy.ipynb) shows how can we encode the energy constraints of ConsMDP into states and actions of a regular MDP. It also briefly discusses the blow-up of the state-space in this conversion.

[Labeled](Labeled.ipynb) presents the labeled framework: ConsMDP with states labeled by sets of propositions, specifications given as deterministic Büchi automata or the recurrence fragment of LTL. You need to have [Spot] and its Python binding installed to run this notebook.

[Solvers](Solvers.ipynb) discusses the energy solvers included in [FiMDP] and it demonstrates impact of these solvers on the quality of strategies from the control perspective. This needs [FiMDPEnv] installed.

[Storm and Prism](StormAndPrism.ipynb) demonstrates the ability of [FiMDP] to read ConsMDPs encoded as PRISM models, or to read Storm models directly. It also covers translation of ConsMDPs into equivalent MDPs in [Storm] (similar to [Explicit energy](ExplicitEnergy.ipynb) notebook). This needs [Storm] and [Stormpy] installed.

[Strategies](Strategies.ipynb) covers strategies, action selectors, simulator, and related structures used through [FiMDP]. It presents the different types of strategies and selectors, and how to use them. It also includes a guide on how to create a new type of strategy.

[Graphviz]: https://graphviz.org/
[FiMDP]: https://github.com/FiMDP/FiMDP/
[FiMDPEnv]: https://github.com/FiMDP/FiMDPEnv
[nbviewer]: https://nbviewer.jupyter.org/
[Storm]: https://www.stormchecker.org/index.html
[Stormpy]: https://moves-rwth.github.io/stormpy/
[Spot]: https://spot.lrde.epita.fr/