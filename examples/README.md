# Examples

This folder contains several notebooks; all of them can be run offline on your machine using [Jupyter] notebook or [Jupyter] lab environment. Alternatively, you can execute the notebooks using [Binder](https://mybinder.org) (no installation needed) online at https://mybinder.org/v2/gh/xblahoud/FiMDP/master. Please note that it takes a few minutes before Binder builds the environment. The notebooks contain pre-executed results that we measured on our hardware, and these can also be explored non-interactively using [nbviewer](https://nbviewer.jupyter.org/) using this [link](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/tree/master/examples/).

## Notebooks' description

The folder contains three types of notebooks:
1. Notebook for CAV artifact evaluation that reproduces the results presented in our paper accepted for presentation at [CAV2020] (Computer-Aided Verification conference 2020).
2. Notebooks that provide more in-depth experiments with two extensive case studies (_NY city traffic_ and _Mars 2020_) prepared for benchmark our algorithms.
3. Notebooks with various examples used in the process of developing this package; the notebooks include tiny examples that explore various objectives, comparison of different approaches to solving the safety objective, discussion on an incorrect approach, and finally, an example that demonstrates the worst-case bound for our positive-reachability algorithm. These notebooks require you to have [GraphViz] installed which is used to render the produced MDPs and the computed values.

### Artifact evaluation
The *[artifact_evaluation](artifact_evaluation.ipynb)* notebook includes the benchmarks in our paper titled *Qualitative Controller Synthesis for Consumption Markov Decision Processes*. It also contains links to instructions on how to use this package. This notebook is meant to aid in the evaluation of this artifact and should be sufficient to reproduce (modulo hardware differences) the presented results.

You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/artifact_evaluation.ipynb) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/artifact_evaluation.ipynb).

### New York City traffic case study
There are two notebooks that present the case study of an electric vehicle routing in NYC. In short, we have an MDP that model moving of the car with varying consumption based on real traffic and consumption data.

1. The [nyc_benchmark](nyc_bechmark.ipynb) notebook experiments with the timing of computation for various objectives using our tool. As the consumption MDP in this example is modeled by a real-world scale network, the computation times obtained in this analysis gives us insights into the practicality of our tools. We analyze how the computation time varies for different parameters (capacity, targets) while calculating strategies.
You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/nyc_benchmark.ipynb>) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/nyc_benchmark.ipynb).

2. The [nyc_visualization](nyc_visualization.ipynb) notebook visually demonstrates strategies for given objectives on an interactive map of Manhattan. 
If you want to preview the precomputed results locally, you must mark the notebook as trusted first.
You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/nyc_visualization.ipynb) (**does not** offer the interactive map) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/nyc_visualization.ipynb) (**does** show the interactive map).

### Mars rover case study
The [mars_benchmark](mars_benchmark.ipynb) presents a case study based on a Mars 2020 mission that features a rover and a quad moving in a grid-world. This case study was designed to reveal the scalability limits of our approach; it generates MDPs with huge state-spaces where the computations can take several minutes. The notebook generates grid-worlds of growing size and measures the computation times of our tool. 

You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/mars_benchmark.ipynb) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/mars_benchmark.ipynb).

### Reachability \& Büchi
The [reach_buchi](reach_buchi.ipynb) notebook explains the available objectives and discusses them visually on an MDP in which we need different initial loads of energy for each objective.

You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/reach_buchi.ipynb) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/reach_buchi.ipynb).

### 2 variants to compute the safety objective
The [safe_variants](safe_variants.ipynb) notebook compares the performance of two algorithms that compute the safety objective with different worst-case complexity. Both variants are based on a fixed-point computation: one on the largets fixed-point and the other on least one. The notebook compares the computation time of both variants for the safety 
objective, discusses the effect on the Büchi objective using the NY city traffic MDP.

You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/safe_variants.ipynb) or  [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/safe_variants.ipynb).

### Incorrect least-bound approach
The [incorrect_least-bound](incorrect_least-bound.ipynb) notebook provides an example of incorrectness of least fixed-point algorithms bounded by :math:`|S|` iterations for the safety objective.

You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/incorrect_least-bound.ipynb) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/incorrect_least-bound.ipynb).

### Worst-case for positive reachability
The [reachability_flower](reachability_flower.ipynb) notebook presents a parametric MDP (shaped as two connected flowers) that reaches the worst-case complexity for our algorithm. It forces a quadratic number of iterations (each iteration has a linear running time) with respect to the number of states in the MDP. The notebook provides diagrams of the MDP states and the energy levels, and it also displays the computation step-by-step which uncovers where the complexity comes from.

You can preview the non-interactive version at [GitHub](https://github.com/xblahoud/FiMDP/blob/master/examples/reachability_flower.ipynb) or [nbviewer](https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/reachability_flower.ipynb).

[jupyter]: https://jupyter.org
[CAV2020]: http://i-cav.org/2020/
[GraphViz]: https://graphviz.org/