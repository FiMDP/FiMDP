FiMDP - Fuel in Markov Decision Processes
==========================================

.. image:: https://travis-ci.org/xblahoud/FiMDP.svg?branch=master
    :target: https://travis-ci.org/xblahoud/FiMDP

Introduction
------------

FiMDP is a Python package designed around a proof-of-concept tool implementing algorithms developed in our work on 
controller synthesis for resource-constrained problems modeled as Consumption Markov Decision Processes (CMDPs). This package includes
interactive Jupyter notebooks with examples modeling real-world problems as CMDPs integrated with our tool. The examples include tests
designed to show the utility and scalability of our algorithms and interactive objects designed to visually evaluate the algorithms.

Authors
-------

This package is based on the work titled `Qualitative Controller Synthesis for Consumption Markov Decision Processes`
by `František Blahoudek <https://www.linkedin.com/in/fanda-blahoudek-392a6752>`_, `Tomáš Brázdil <https://cz.linkedin.com/in/tom%C3%A1%C5%A1-br%C3%A1zdil-23959766>`_, 
`Petr Novotný <https://www.fi.muni.cz/~xnovot18/>`_, `Melkior Ornik <https://mornik.web.illinois.edu/>`_, `Pranay Thangeda <https://www.pranaythangeda.com/>`_,
and `Ufuk Topcu <https://www.ae.utexas.edu/facultysites/topcu/wiki/index.php/Main_Page>`_. This package is developed and maintained by `František Blahoudek <mailto:fandikb@gmail.com>`_ and `Pranay Thangeda <mailto:contact@prny.me>`_.

Overview
---------

.. note:: This overview assumes no background in the topic and tries to explains the problem     in layman terms. For a detailed explanation of our work,
          please go through our paper titled *Qualitative Controller Synthesis for Consumption Markov Decision Processes*.

Several real-world systems of interest are resource constrained, i.e., they utilize certain resource from a limited supply that must be replenished regularly.
For example, autonomous electric systems such as driverless cars, autonomous drones, planetary rovers, etc, are constrained by design to operate on power drawn 
from a battery of limited capacity and resource exhaustion could potentially lead to several undesirable consequences including safety hazards. Further, such
systems usually operate in uncertain environments with stochastic dynamics that can be effectively modeled as Markov decision process (MDPs). 

Traditionally, resource-constrained systems were studied using so called *energy* based models that are known not to admit 
polynomial-time controller synthesis algorithms. We instead build up-on so called *consumption* models that typically admit
more efficient analysis and extend it to probabilistic setting. A consumption MDP (CMDP) is then characterized 
by an MDP that models the stochastic environment, the capacity of the agent, and the initial resource level. Given a CMDP with no zero-consumption cycles, and a set 
of target states, we show that we can prove in polynomial time the existence of a strategy that prevents resource exhaustion and 
visits some target states infinitely often. If such a strategy exists, we provide its polynomial-size representation in polynomial-time.

.. raw:: html

    <iframe src="_static/strategy.html" allowfullscreen=true height="405px" width="100%"></iframe>

The interactive map above visualizes an example CMDP and the strategy obtained from our algorithm. **Zoom in** to see
the action choices at different states (intersections) for different energy levels. The green nodes indicate reload states, 
the blue nodes indicate target states, and the red nodes are states where no particular action is specified by the
strategy. A detailed description of this example is provided in the examples section :ref:`examples`.

Installation
------------
The tool is written in Python 3 and the examples are presented using interactive Jupyter notebooks.
We offer several different ways to access the examples in our package. You can find detailed installation
and usage instructions at this page :ref:`install`.

**Binder**: Directly access the Jupyter notebooks with examples in web browser without any explicit installation. 
This is the quickest and easiest option to get started. 

**Docker**: Run the docker image with the package published at Docker Hub and and access the Jupyter notebooks with examples on your local machine.

**Conda Installation**: Use conda to create a new conda virtual environment using the requirements.txt file and access
examples via Jupyter notebook server on your local machine.

**Pip Installation**: Clone the repository and install the dependencies with pip3. Access notebooks via Jupyter notebook running
on your local machine.

.. note:: If you are installing the tool on your machine, you also need to separately install `GraphViz <https://www.graphviz.org/>`_ 
          and add the *dot* to your system PATH for running certain examples. 

Examples
--------
We provide a number of examples in Interactive Jupyter notebooks to explore the features of our tool, to 
analyze its performance, and also to validate the results presented in our paper. The two primary examples are 
the problems of an electric vehicle routing with limited capacity and a multi-agent grid world inspired by the 
Mars 2020 mission. For detailed description of the problems and the example notebooks, visit the examples section :ref:`examples`.

.. figure:: /images/environments.png
   :alt: environments demo
   :scale: 70%
   :align: center 

   The two primary examples: multi-agent grid world (left) and electric vehicle routing (right).

Citation Info
-------------
This package supplements our work that has been accepted to the 32nd International Conference on Computer-Aided Verification (`CAV 2020 <http://i-cav.org/2020/>`_) 
scheduled to take place July 19-24, 2020. Citation info will be updated once the conference proceedings are available online. 

Support
-------
Detailed documentation of the modules has been provided in the documentation section :ref:`docs`. If you have any trouble with the installation, 
or have any questions, raise an issue in `GitHub <https://github.com/xblahoud/FiMDP>`_ or email `František Blahoudek <mailto:fandikb@gmail.com>`_ or `Pranay Thangeda <mailto:contact@prny.me>`_.

License
-------
This package is released under the highly permissive MIT license which also makes it clear that the authors
and the organizations they are a part of cannot be held liable to any damage caused by usage of this 
package or any topic discussed in it. For a detailed statement, go through the license file: :ref:`license`.

Detailed Contents
-----------------
.. toctree::
   :maxdepth: 2

   install
   examples
   license
   fimdp_autodoc   

Indices and Search
-------------------

* :ref:`genindex`
* :ref:`search`