.. _examples:

Examples
===========

.. note:: All the examples can be run offline on your machine using Jupyter notebook. 
    In this section, we provide links to the notebooks in the repository to view
    precalculated results. You can access interactive versions of the notebooks using
    Binder at this `link <https://mybinder.org/v2/gh/pthangeda/consumption-MDP/master>`_. 
    It takes a few minutes before the Binder environment gets loaded.
    

In this section, we provide a short description of the tasks performed in each of the example notebook. We also 
note that these notebooks also have detailed notes within for ease of understanding.

safe_variants
***************
The *safe_variants* notebook helps in comparing the performance of the two variants for computing the safe vector for a given capacity. The 
notebook compares the computation time of both variants using safety and Büchi objectives for different values of capacities.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/safe_variants.ipynb>`_ to preview the *safe_variants* notebook.

nyc_benchmark
*************
The *nyc_benchmark* notebook hosts experiments related to calculating the computational time for different algorithms and objectives in our tool. 
As the consumption MDP in this example is modeled by a real-world scale network, the computational times obtained in this analysis gives us 
insights into the practicality of our tools. We also analyze how the computational time varies for different parameters while calculating strategies.
Further details about the tests performed in this example are mentioned in the notebook.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/nyc_benchmark.ipynb>`_ to preview the *nyc_benchmark* notebook.

mars_benchmark
***************
The *mars_benchmark* notebook hosts experiments depicting how our tool scales with the size of the state space. As mentioned earlier, in this model
we have two agents interacting with each other on a 2D grid world. In this case, the number of states in the state-space grow sharply with the size of the
grid. 

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/mars_benchmark.ipynb>`_ to preview the *mars_benchmark* notebook.

incorrect_least-bound
**********************
The *incorrect_least-bound** notebook provides example of incorrectness of a least fixed point algorithm bounded by |S| and also hosts an
example that shows that |S| iteration is also incorrect when used for least fixed_point that computes survival levels.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/incorrect_least-bound.ipynb>`_ to preview the *incorrect_least-bound* notebook.

kucera_example
***************
The *kucera_example* notebook hosts an example MDP with a function to visualize the energy levels required at states for different objectives. The results are
visualized using GraphViz package.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/kucera_example.ipynb>`_ to preview the *kucera_example* notebook.

reachability_example
********************
The *reachability_example* notebook includes simple MDP examples to help distinguish between different objectives in an intuitive fashion.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/reachability_example.ipynb>`_ to preview the *reachability_example* notebook.

reachability_flower
********************
The *reachability_flower* notebook hosts the example of a double flower shaped consumption MDP. It displays step by step results to visualize the 
evolution of computation over the steps.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/reachability_flower.ipynb>`_ to preview the *reachability_flower* notebook.

reach_buchi
***************
The *reach_buchi* notebook hosts an example on reachability and Büchi objectives anf also helps in distinguishing positive reachability, almost-sure reachability and Büchi 
objectives. It visualizes the graph of MDP using GraphViz for ease of understanding.

`Click here <https://github.com/pthangeda/consumption-MDP/blob/master/examples/reach_buchi.ipynb>`_ to preview the *reach_buchi* notebook.

