
# FiMDP - Fuel in Markov Decision Processes
**Python Package with Algorithms for Controller Synthesis in Resource-constrained Markov Decision Processes**

[![Documentation Status](https://readthedocs.org/projects/fimdp/badge/?version=latest)](https://fimdp.readthedocs.io/en/latest/?badge=latest) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/xblahoud/FiMDP/master?urlpath=lab) [![Build Status](https://travis-ci.org/xblahoud/FiMDP.svg?branch=master)](https://travis-ci.org/xblahoud/FiMDP)

**FiMDP** is a Python package for analysis and controller synthesis of Consumption Markov Decision Processes (ConsMDPs) — MDPs with resource constraints. The model of ConsMDPs and the basic algorithms implemented in FiMDP are described in our paper presented at CAV2020 [[1]](#1).

Our related project called **[FiMDPEnv]** is a set of environments that work with FiMDP and can create animations like this one.
<p align="center">
<img src="https://github.com/FiMDP/FiMDP/blob/master/docs/source/images/demoanimation.gif" alt="Multiple agents following energy-aware policy in grid-world." align="center" height="250" width="350" >
<br>
<em>Multiple agents following energy-aware policies in UUVEnv from <a href="https://github.com/FiMDP/FiMDPEnv">FiMDPEnv</a>.  </em>
</p>

## Installation

FiMDP can be installed using pip from PyPI
```
pip install -U fimdp
```
While the baseline package has minimal dependencies, FiMDP depends on several other tools for extended functionality. Some of the recommended dependencies are:

* [Graphviz]: for visualizations in Jupyter notebooks,
* [Storm] and [Stormpy]: for reading PRSIM, JANI, and Storm models,
* [Spot](https://spot.lrde.epita.fr/): for support of labeled ConsMDPs and specifications given as deterministic Büchi automata or the recurrence fragment of Linear-time Temporal Logic (LTL).

## Usage and documentation (work in progress)

The directory [tut](tut/README.md) contains several notebooks that explain how to use FiMDP. The notebook [Basics.ipynb](tut/Basics.ipynb) is a good starting point.

For a complete overview of the tool, installation options, source code documentation, and interactive examples refer to [FiMDP readthedocs].


## Evaluations
Notebooks evaluationg performance of FiMDP are stored in a separate repository 
[FiMDP-Evaluation].


## Contact
If you have any trouble with the installation, or have any questions, raise an issue or email [František (Fanda) Blahoudek](fandikb+dev@gmail.com) or [Pranay Thangeda](contact@prny.me).

## References
<a id="1">[1]</a> 
Blahoudek F., Brázdil T., Novotný P., Ornik M., Thangeda P., Topcu U. (2020) **Qualitative Controller Synthesis for Consumption Markov Decision Processes.** In proceeding of CAV 2020. Lecture Notes in Computer Science, vol 12225. Springer. https://doi.org/10.1007/978-3-030-53291-8_22


[FiMDP-Evaluation]: https://github.com/FiMDP/FiMDP-Evaluation
[FiMDP readthedocs]: https://fimdp.readthedocs.io/
[FiMDPEnv]: https://github.com/FiMDP/FiMDPEnv
[Graphviz]: https://graphviz.org/
[Storm]: https://www.stormchecker.org/index.html
[Stormpy]: https://moves-rwth.github.io/stormpy/
[Spot]: https://spot.lrde.epita.fr/
