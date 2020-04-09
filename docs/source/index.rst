CMDP - Consumption MDP Package
===============================

.. image:: https://travis-ci.org/pthangeda/consumption-MDP.svg?branch=master
    :target: https://travis-ci.org/pthangeda/consumption-MDP

Introduction
------------

CMDP is a collection of Python modules that implement algorithms developed in our work on controller synthesis for 
resource-constrained problems modeled as consumption Markov decision processes. Consumption Markov Decision 
Processes are probabilistic decision-making models of resource-constrained systems and naturally model many 
interesting real-world problems. This package includes examples based on two such realistic problems and also 
includes additional examples that present specific nuisances of the algorithm. 

Authors
-------
This package is based on the work titled `Qualitative Controller Synthesis for Consumption Markov Decision Processes`
by František Blahoudek, Tomáš Brázdil, Petr Novotný, Melkior Ornik, Pranay Thangeda and Ufuk Topcu. Most of code is this 
package is developed by František Blahoudek and is maintained by `František Blahoudek <mailto:fandikb@gmail.com>`_ and `Pranay Thangeda <mailto:contact@prny.me>`_.

Overview
---------

.. note:: This overview assumes no background in the problem of interest and hence is close to layman terms. For a more detailed read,
         please go through our work titled *Qualitative Controller Synthesis for Consumption Markov Decision Processes* on which is package
         is based. 

Several real-world problems are inherently stochastic and can be aptly modeled as consumption Markov Decision Processes (CMDPs). Describe
the utility of such a model and the importance of our contributions. Use the example html file to clarify the relevance of such problems
in real-world while providing a brief description of the case-study and providing link to detailed description in examples section.

.. raw:: html

    <iframe src="_static/strategy.html" allowfullscreen=true height="545px" width="100%"></iframe>
     Interactive map visualizing the strategy for the electric vehicle routing MDP.


Installation
------------
The tool is written in Python 3 and the examples are presented using interactive Jupyter notebooks.
We offer several different ways to access the examples in our package. You can find detailed installation
and usage instructions at this page :ref:`install`.

**Binder**: Directly access the Jupyter notebooks with examples in web browser without any explicit installation. 
This is the quickest and easiest option to get started. 

**Docker**: Provide link to the docker image and instructions on accessing the essential files.

**Conda Installation**: Use conda to creat   e a new conda virtual environment using the requirements.txt file and access
examples via Jupyter notebook server on your local machine.

**Pip Installation**: Clone the repository and install the dependencies with pip3. Access notebooks via Jupyter notebook running
on your local machine.

.. note:: If you are installing the tool on your machine, you also need to separately install `GraphViz <https://www.graphviz.org/>`_ 
          and add the *dot* to your system PATH for running certain examples. 

Examples
--------
We provide a number of interactive examples as Jupyter notebooks to explore the features of our tool and also to 
analyze its performance. The two main examples model the problems of an autonomous electric vehicle with limited 
capacity navigating the streets of Manhattan, New York and a Martian rover and aerial vehicle with limited
capacity and different dynamics operating in a grid world of variable size. For detailed description of the 
problems and the example notebooks, visit the examples section :ref:`examples`.

Citation Info
-------------
This work has been accepted to the 32nd International Conference on Computer-Aided Verification (`CAV 2020 <http://i-cav.org/2020/>`_) scheduled to take place
July 19-24, 2020. Citation info will be updated once the conference proceedings are available online. 

Support
-------
Detailed documentation of the modules has been provided in the documentation section :ref:`docs`. If you have any trouble with the installation, 
or have any questions, raise an issue in `GitHub <https://github.com/pthangeda/consumption-MDP>`_ or email `František Blahoudek <mailto:fandikb@gmail.com>`_ or `Pranay Thangeda <mailto:contact@prny.me>`_.

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
   cmdp_autodoc   

Indices and Search
-------------------

* :ref:`genindex`
* :ref:`search`