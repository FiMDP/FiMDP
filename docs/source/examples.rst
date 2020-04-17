.. _examples:

Examples
=========

.. note:: All the examples can be run offline on your machine using Jupyter notebook. 
    In this section, we provide links to the notebooks in the repository to view
    pre-executed results. You can access interactive versions of the notebooks using
    Binder at this `link <https://mybinder.org/v2/gh/xblahoud/FiMDP/master>`_. 
    It takes a few minutes for the Binder environment to load.

Case-studies Description
------------------------
In this section, we briefly describe the two important environments considered as case-studies in our work. The environments
model real-world problems and are used to demonstrate the utility and scalability of the proposed algorithm.

Electric Vehicle Routing
************************

* `Click here <https://github.com/xblahoud/FiMDP/blob/master/examples/nyc_benchmark.ipynb>`_ to preview the notebook with tests for benchmarking this environment.
* `Click here <https://github.com/xblahoud/FiMDP/blob/master/examples/nyc_visualization.ipynb>`_ to preview the notebook that visualizes strategies on an interactive map.

Routing of autonomous electric vehicles presents a significant challenge due to their limited driving range and 
low availability of recharge stations. Further, the rate of energy consumption depends on several variables that are
often stochastic. We consider an area in the middle of Manhattan, from 42nd to 116th Street, given in the figure below, 
with the agent’s original state space consisting of street intersections. The agent’s actions — turns performed at these intersections — result
in deterministic transitions to subsequent states, but with stochastic consumption of energy, depending on traffic. 
We model the consumption on each edge by using data on distributions of vehicle travel times and velocity and converting them to discrete energy energy consumption values.
Since the CMDP framework only allows for deterministic consumption, we introduce pseudo-states to create a CMDP from our MDP and energy consumption distributions.
The states in the proximity of real-world fast charging stations in the area are considered as reload states in the CMDP. Creating a CMDP from the street network
graph of the area shown in the figure below, we obtain a CMDP with 7378 states.

.. figure:: /images/nycmap.png
   :alt: AEV for NYC
   :scale: 70%
   :align: center 

   Manhattan street network considered as the operating domain for electric vehicle routing MDP. Red dots indicate the reload states, i.e.,
   electric-vehicle charging stations. Green edges indicate one-way roads.


Multi-agent Grid world
**********************

* `Click here <https://github.com/xblahoud/FiMDP/blob/master/examples/mars_benchmark.ipynb>`_ to preview the notebook with tests for benchmarking this environment.

This case-study explores a multi-agent scenario of a rover and a helicopter operating on Mars. The
narrative of the case study is informed by realistic considerations of the Mars 2020 mission. 
Namely, we consider a rover of infinite energy capacity and a helicopter of finite capacity that recharges 
by returning to the rover. These two vehicle jointly operate on a mission where the helicopter needs to reach 
areas inaccessible to the rover. We assume that the outcomes of all the actions of the helicopter are 
deterministic while those of the rover — influenced by terrain dynamics — are stochastic. For the purpose
of this experiment, we specify that every transition of the helicopter costs 1 energy unit. For a grid world of size :math:`n`, 
this system can be naturally modeled as a CMDP with :math:`n^4` states (representing the x- and y-coordinates of the 
rover and the helicopter). This case-study is primarily used to study the scalability limits of the proposed algorithms.

.. only:: html

   .. figure:: /images/marsenv.gif
      :scale: 90%
      :align: center 

      Mars multi-agent grid world example with states that are unreachable for the rover. 

Examples Description
--------------------
In this section, we provide a short description of the tasks performed in each of the example notebook. We also 
note that the notebooks themselves have detailed description of the objective and the modules utilized. There are three types of notebooks:

1. Notebook for CAV artifact evaluation that reproduces the results presented in our paper accepted for presentation at `CAV2020 <http://i-cav.org/2020/>`_ (Computer-Aided Verification conference 2020).
2. Notebooks that provide more in-depth experiments with two extensive case studies described above for benchmark our algorithms.
3. Notebooks with various examples used in the process of developing this package; the notebooks include tiny examples that explore various objectives, comparison of different approaches to solving the safety objective, discussion on an incorrect approach, and finally, an example that demonstrates the worst-case bound for our positive-reachability algorithm. These notebooks require you to have [GraphViz] installed which is used to render the produced MDPs and the computed values.

Artifact evaluation
*******************
The artifact_evaluation notebook includes the benchmarks in our paper titled *Qualitative Controller Synthesis for Consumption Markov Decision Processes*. It also contains links to instructions on how to use this package. This notebook is meant to aid in the evaluation of this artifact and should be sufficient to reproduce (modulo hardware differences) the presented results.

You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/artifact_evaluation.ipynb>`_ or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/artifact_evaluation.ipynb>`_.

New York City traffic case study
********************************
There are two notebooks that present the case study of an electric vehicle routing in NYC. In short, we have an MDP that model moving of the car with varying consumption based on real traffic and consumption data.

1. The nyc_benchmark notebook experiments with the timing of computation for various objectives using our tool. As the consumption MDP in this example is modeled by a real-world scale network, the computation times obtained in this analysis gives us insights into the practicality of our tools. We analyze how the computation time varies for different parameters (capacity, targets) while calculating strategies.
You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/nyc_benchmark.ipynb>`_ or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/nyc_benchmark.ipynb>`_.

2. The nyc_visualization notebook visually demonstrates strategies for given objectives on an interactive map of Manhattan. 
If you want to preview the precomputed results locally, you must mark the notebook as trusted first.
You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/nyc_visualization.ipynb>`_ (**does not** offer the interactive map) or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/nyc_visualization.ipynb>`_ (**does** show the interactive map).

Mars rover case study
*********************
The mars_benchmark presents a case study based on a Mars 2020 mission that features a rover and a quad moving in a grid-world. This case study was designed to reveal the scalability limits of our approach; it generates MDPs with huge state-spaces where the computations can take several minutes. The notebook generates grid-worlds of growing size and measures the computation times of our tool. 

You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/mars_benchmark.ipynb>`_ or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/mars_benchmark.ipynb>`_.

Reachability \& Büchi
**********************
The reach_buchi notebook explains the available objectives and discusses them visually on an MDP in which we need different initial loads of energy for each objective.

You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/reach_buchi.ipynb>`_ or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/reach_buchi.ipynb>`_.

2 variants to compute the safety objective
********************************************
The safe_variants notebook compares the performance of two algorithms that compute the safety objective with different worst-case complexity. Both variants are based on a fixed-point computation: one on the largets fixed-point and the other on least one. The notebook compares the computation time of both variants for the safety 
objective, discusses the effect on the Büchi objective using the NY city traffic MDP.

You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/safe_variants.ipynb>`_ or  `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/safe_variants.ipynb>`_.

Incorrect least-bound approach
*******************************
The incorrect_least-bound notebook provides an example of incorrectness of least fixed-point algorithms bounded by :math:`|S|` iterations for the safety objective.

You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/incorrect_least-bound.ipynb>`_ or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/incorrect_least-bound.ipynb>`_.

Worst-case for positive reachability
*************************************
The reachability_flower notebook presents a parametric MDP (shaped as two connected flowers) that reaches the worst-case complexity for our algorithm. It forces a quadratic number of iterations (each iteration has a linear running time) with respect to the number of states in the MDP. The notebook provides diagrams of the MDP states and the energy levels, and it also displays the computation step-by-step which uncovers where the complexity comes from.

You can preview the non-interactive version at `GitHub <https://github.com/xblahoud/FiMDP/blob/master/examples/reachability_flower.ipynb>`_ or `nbviewer <https://nbviewer.jupyter.org/github/xblahoud/FiMDP/blob/master/examples/reachability_flower.ipynb>`_.


