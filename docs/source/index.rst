CMDP - Consumption MDP Package
===============================

Introduction
------------

CMDP is a Python package that implements algorithms developed in our work on controller synthesis for 
resource-constrained problems modeled as consumption Markov decision processes. Consumption Markov Decision 
Processes are probabilistic decision-making models of resource-constrained systems and naturally model many 
interesting real-world problems. This package includes examples based on two such realistic problems and also 
includes additional examples that present specific nuisances of the algorithm. 

Authors
-------
This package is based on the work titled `Qualitative Controller Synthesis for Consumption Markov Decision Processes`
by František Blahoudek, Tomáš Brázdil, Petr Novotný, Melkior Ornik, Pranay Thangeda and Ufuk Topcu. Most of code is this 
package is developed by František Blahoudek and is maintained by `František Blahoudek <mailto:fandikb@gmail.com>`_ and `Pranay Thangeda <mailto:contact@prny.me>`_.

Citation Info
-------------
Coming soon.

Installation
------------
The tool is written in Python 3 and the examples are presented using interactive Jupyter notebooks.
We offer several different ways to access the examples in our package. You can find detailed installation
and usage instructions at this page :ref:`install`.

**Binder**: Directly access the Jupyter notebooks with examples in web browser without any explicit installation. 
This is the quickest and easiest option to get started. 

**Pip Installation**: Clone the repository and install the dependencies with pip3. Access notebooks via Jupyter notebook running
on your local machine.

**Conda Installation**: Use conda to creat   e a new conda virtual environment using the requirements.txt file and access
examples via Jupyter notebook server on your local machine.

.. note:: If you are installing the tool on your machine, you also need to separately install `GraphViz <https://www.graphviz.org/>`_ and add the *dot* to your system PATH for running certain examples. 


Examples
--------
We provide a number of interactive examples as Jupyter notebooks to explore the features of our tool and also to analyze its performance. The two main examples model
the problems of an autonomous electric vehicle with limited capacity navigating the streets of Manhattan, New York and a Martian rover and aerial vehicle with limited
capacity and different dynamics operating in a grid world of variable size. For detailed description of the problems and the example notebooks, visit the examples section
:ref:`examples`.

Support
-------
If you have any trouble with the installation, or have any questions, raise an issue in GitHub or email 
`František Blahoudek <mailto:fandikb@gmail.com>`_ or `Pranay Thangeda <mailto:contact@prny.me>`_.

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

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


HTML Test
---------
.. raw:: html

    <iframe src="_static/strategy.html" height="845px" width="100%"></iframe>
