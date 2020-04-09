
# CMDP
**Python Package with Algorithms for Controller Synthesis in Consumption Markov Decision Processes**

[![Documentation Status](https://readthedocs.org/projects/cmdp/badge/?version=latest)](https://cmdp.readthedocs.io/en/latest/?badge=latest) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pthangeda/consumption-MDP/master) [![Build Status](https://travis-ci.org/pthangeda/consumption-MDP.svg?branch=master)](https://travis-ci.org/pthangeda/consumption-MDP)


Full overview of the tool, installation options, documentation, and interactive examples:
[CMDP readthedocs](https://cmdp.readthedocs.io/).

**Citation Info**: This work has been accepted to the 32nd International Conference on Computer-Aided Verification ([CAV 2020](http://i-cav.org/2020/)) scheduled to take place
July 19-24, 2020. Citation info will be updated once the conference proceedings are available online. 


## Overview

**CMDP** is a Python package that implements algorithms developed in our work on controller synthesis for 
resource-constrained problems modeled as consumption Markov decision processes. The algorithms are 
detailed in the work titled 'Qualitative Controller Synthesis for Consumption Markov Decision Processes' by 
František Blahoudek, Tomáš Brázdil, Petr Novotný, Melkior Ornik, Pranay Thangeda and Ufuk Topcu.

## Installation and Usage

**Binder**
Use this [link](https://mybinder.org/v2/gh/pthangeda/consumption-MDP/master) to access the interactive Jupter notebooks on the web without any installation.

**Local Installation**
Refer to the [installation documentation](https://cmdp.readthedocs.io/en/latest/install.html).

## Example Environments
We provide a number of interactive examples as Jupyter notebooks to explore the features of our tool and also to analyze its performance. 
The two main examples model the problems of an autonomous electric vehicle with limited capacity navigating the streets of Manhattan, New York and 
a Martian rover and aerial vehicle with limited capacity and different dynamics operating in a grid world of variable size. 
The notebook can be found in the `examples` subdirectory.

![The two case-studies considered: Electric Vehicle Routing and Multi-agent Grid World.](https://raw.githubusercontent.com/pthangeda/consumption-MDP/master/docs/source/images/environments.png)


## Documentation
Documentation available at [readthedocs](https://cmdp.readthedocs.io/).

## Contact
If you have any trouble with the installation, or have any questions, raise an issue or email [František Blahoudek](fandikb@gmail.com) or [Pranay Thangeda](contact@prny.me).



