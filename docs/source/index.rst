CMDP - Consumption MDP Package
===============================

Introduction
------------

CMDP is a Python package that implements a polynomial-time controller synthesis algorithm for 
resource-constrained problems modeled as consumption Markov decision processes. The algorithm is detailed
in the work titled 'Qualitative Controller Synthesis for Consumption Markov Decision Processes' by 
František Blahoudek, Tomáš Brázdil, Petr Novotný, Melkior Ornik, Pranay Thangeda and Ufuk Topcu.


Citation Info
-------------
Coming soon.

Support
-------
If you have any trouble with the installation, or have any quesions, raise an issue or email 
`František Blahoudek <mailto:fandikb@gmail.com>`_ or `Pranay Thangeda <mailto:contact@prny.me>`_.

License
-------
This package is released under the highly permissive MIT license which also makes it clear that the authors
and the organizations they are a part of cannot be held liable to any damage caused by usage of this 
package or any topic discussed in it. For a detailed statement, go through the license file: :ref:`license`.

Installation
------------
Install via pip or use the provided docker image. You could also launch the example notebooks on
binder for a installation-free use. 
:ref:`install`.

Examples
--------
The examples cover two realistic domains of an autonomous electric taxi in the streets of Manhattan, NY
and a simplified model of rover and helicopter multi-agent system operating on Martian surface. 
:ref:`examples`.

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