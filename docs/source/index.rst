FiMDP - Fuel in Markov Decision Processes
==========================================

.. image:: https://travis-ci.org/FiMDP/FiMDP.svg?branch=master
    :target: https://travis-ci.org/FiMDP/FiMDP

Introduction
------------

`FiMDP <https://github.com/FiMDP/FiMDP>`_ is a Python package for analysis and controller synthesis of Markov decision processes with resource constraints, 
modeled as Consumption Markov Decision Processes (ConsMDPs). The model of ConsMDPs and associated algorithms were first introduced in
our work titled `Qualitative Controller Synthesis for Consumption Markov Decision Processes` presented at CAV2020  :ref:`Citation Info`. 

This package includes interactive Jupyter notebooks with examples from `FiMDPEnv`_, our related project that provides 
realistic simulation environments that model real-world ConsMDPs. The package also includes tutorials designed to help you get started with our tool.

Authors
-------

This package is developed and maintained by `František Blahoudek <https://www.linkedin.com/in/fanda-blahoudek-392a6752>`_, and 
`Pranay Thangeda <https://www.pranaythangeda.com/>`_. Contact information is provided in the section :ref:`Support`.

---------

.. note:: This overview assumes no background in the topic and tries to explains the problem in layman terms. For a detailed explanation of our work,
          please go through our paper :ref:`Citation Info`. 

Several real-world systems of interest are resource constrained, i.e., they utilize certain resource from a limited supply that must be replenished regularly.
For example, autonomous electric systems such as driverless cars, autonomous drones, planetary rovers, etc, are constrained by design to operate on power drawn 
from a battery of limited capacity and resource exhaustion could potentially lead to several undesirable consequences including safety hazards. Further, such
systems usually operate in uncertain environments with stochastic dynamics that can be effectively modeled as Markov decision process (MDPs). 

Traditionally, resource-constrained systems were studied using so called *energy* based models that are known not to admit 
polynomial-time controller synthesis algorithms. We instead build up-on so called *consumption* models that typically admit
more efficient analysis and extend it to probabilistic setting. A consumption MDP (ConsMDP) is then characterized 
by an MDP that models the stochastic environment, the capacity of the agent, and the initial resource level. Given a ConsMDP with no zero-consumption cycles, and a set 
of target states, we show that we can prove in polynomial time the existence of a strategy that prevents resource exhaustion and 
visits some target states infinitely often. If such a strategy exists, we provide its polynomial-size representation in polynomial-time.

.. raw:: html

    <iframe src="_static/strategy.html" allowfullscreen=true height="405px" width="100%"></iframe>

The interactive map above visualizes an example ConsMDP and the strategy obtained from our algorithm. **Zoom in** to see
the action choices at different states (intersections) for different energy levels. The green nodes indicate reload states, 
the blue nodes indicate target states, and the red nodes are states where no safe action is prescribed by the strategy at the 
current energy level. 

Installation
------------
FiMDP is written in Python 3 and the examples are presented using interactive Jupyter notebooks.
FiMDP can be installed using pip from PyPI:

:code:`pip install -U fimdp`

While the baseline package has minimal dependencies, FiMDP depends on several other tools for extended functionality. Some of the recommended dependencies are:

* `Graphviz`_: for visualizations in Jupyter notebooks,
* `Storm`_ and `Stormpy`_: for reading PRSIM, JANI, and Storm models,
* `Spot`_: for support of labeled ConsMDPs and specifications given as deterministic Büchi automata or the recurrence fragment of Linear-time Temporal Logic (LTL).

Citation Info
-------------
This tool is based on original paper that introduces the notion of ConsMDPs and also presents associated algorithms and guarantees. 
To cite our work on ConsMDPs please use the following publication: 

Blahoudek F., Brázdil T., Novotný P., Ornik M., Thangeda P., Topcu U. (2020) 
**Qualitative Controller Synthesis for Consumption Markov Decision Processes**, 
in proceedings of 32nd International Conference on Computer-Aided Verification (`CAV 2020 <http://i-cav.org/2020/>`_),
Lecture Notes in Computer Science, vol 12225. Springer. https://doi.org/10.1007/978-3-030-53291-8_22

Support
-------
Detailed documentation of the modules has been provided in the :ref:`docs` section. If you have any trouble with the installation, 
or have any questions, raise an issue in `GitHub <https://github.com/FiMDP/FiMDP>`_ or email `František Blahoudek <mailto:fandikb@gmail.com>`_ 
or `Pranay Thangeda <mailto:contact@prny.me>`_.

License
-------
This package is released under the highly permissive MIT license which also makes it clear that the authors
and the organizations they are a part of cannot be held liable to any damage caused by usage of this 
package or any topic discussed in it. For a detailed statement, go through the license file - :ref:`licensefile`.


Detailed Contents
-----------------
.. toctree::
   :maxdepth: 2

   fimdp_autodoc   
   license


Indices and Search
-------------------

* :ref:`genindex`
* :ref:`search`


.. _FiMDPEnv: https://github.com/FiMDP/FiMDPEnv
.. _Graphviz: https://graphviz.org/
.. _Storm: https://www.stormchecker.org/index.html
.. _Stormpy: https://moves-rwth.github.io/stormpy/
.. _Spot: https://spot.lrde.epita.fr/