.. _examples:

Examples
=========

.. note:: All the examples can be run offline on your machine using Jupyter notebook. 
    In this section, we provide links to the notebooks in the repository to view
    pre-executed results. You can access interactive versions of the notebooks using
    Binder at this `link <https://mybinder.org/v2/gh/pthangeda/consumption-MDP/master>`_. 
    It takes a few minutes for the Binder environment to load.

Case-studies Description
------------------------
In this section, we briefly describe the two important environments considered as case-studies in our work. The environments
model real-world problems and are used to demonstrate the utility and scalability of the proposed algorithm.

Electric Vehicle Routing
************************
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

      Mars multi-agent grid world example with unreachable states. 

Examples Description
--------------------
In this section, we provide a short description of the tasks performed in each of the example notebook. We also 
note that the notebooks themselves have detailed description of the objective and the modules utilized.

nyc_benchmark
*************
The *nyc_benchmark* notebook hosts experiments related to calculating the computation time for different algorithms and objectives in our tool. 
In particular, we use the electric vehicle routing in NYC as the MDP for all the tests in this notebook. As the consumption MDP in this example 
is modeled by a real-world scale network, the computation times obtained in this analysis gives us insights into the practicality of our tools. 
We analyze how the computation time varies for different parameters while calculating strategies. Further details about the tests performed in 
this example are mentioned in the notebook.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/nyc_benchmark.ipynb>`_ to preview the *nyc_benchmark* notebook.

nyc_visualization
******************
The *nyc_visualization* notebook visually demonstrates strategies obtained for different objectives, using different solvers for the MDP modeling
electric vehicle routing in Manhattan, New York city. The strategy is visualized on an interactive map highlighting reload states, target states 
and the dependency of the action taken on the energy levels. 

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/nyc_visualization.ipynb>`_ to preview the *nyc_visualization* notebook.

mars_benchmark
***************
The *mars_benchmark* notebook hosts experiments depicting how our tool scales with the size of the state space. As mentioned earlier, in this model
we have two agents interacting with each other on a 2D grid world. In this case, the number of states in the state-space grow sharply with the size of the
grid. 

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/mars_benchmark.ipynb>`_ to preview the *mars_benchmark* notebook.

safe_variants
**************
The *safe_variants* notebook helps in comparing the performance of the two variants of solvers for computing the safe vector which specifies
the level of energy need to survive with a given capacity. The notebook compares the computation time of both variants for resource-safety 
and Büchi objectives considering the MDP modeling AEV routing in Manhattan and another small MDP defined in the notebook. Users can modify
the capacity and the MDP itself based the example MDP provided in the notebook and observe the variation in computation for both methods.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/safe_variants.ipynb>`_ to preview the *safe_variants* notebook.

reach_buchi
************
The *reach_buchi* notebook hosts examples covering reachability and Büchi objectives while distinguishing positive reachability and almost-sure reachability.
The notebook includes detailed plots of the example MDP states specifying the energy level needed for different objectives. Running the examples in this
notebook requires installation of GraphViz if you are running it on a local server.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/reach_buchi.ipynb>`_ to preview the *reach_buchi* notebook.

reachability_flower
********************
The *reachability_flower* notebook considers the example of a double flower shaped consumption MDP. The tests in this notebook are primarily based
on the positive reachability objective. It provides detailed plots of the MDP states and the energy levels and also displays step by step results 
to visualize the evolution of computation for a smaller double-flower shaped consumption MDP. Running the examples in this
notebook requires installation of GraphViz if you are running it on a local server.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/reachability_flower.ipynb>`_ to preview the *reachability_flower* notebook.

incorrect_least-bound
**********************
The *incorrect_least-bound** notebook provides example of incorrectness of a least fixed point algorithm bounded by :math:`|S|` and also hosts an
example that shows that :math:`|S|` iteration bound is also incorrect when used for least fixed_point that computes survival levels.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/incorrect_least-bound.ipynb>`_ to preview the *incorrect_least-bound* notebook.



