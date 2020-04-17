
# FiMDP - Fuel in Markov Decision Processes
**Python Package with Algorithms for Controller Synthesis in Resource-constrained Markov Decision Processes**

[![Documentation Status](https://readthedocs.org/projects/fimdp/badge/?version=latest)](https://fimdp.readthedocs.io/en/latest/?badge=latest) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/xblahoud/FiMDP/master) [![Build Status](https://travis-ci.org/xblahoud/FiMDP.svg?branch=master)](https://travis-ci.org/xblahoud/FiMDP)


Full overview of the tool, installation options, documentation, and interactive examples:
[FiMDP readthedocs](https://fimdp.readthedocs.io/).

**Citation Info**: This work has been accepted to the 32nd International Conference on Computer-Aided Verification ([CAV 2020](http://i-cav.org/2020/)) scheduled to take place
July 19-24, 2020. Citation info will be updated once the conference proceedings are available online. 


## Overview

**FiMDP** is a Python package designed around a proof-of-concept tool implementing algorithms developed in our work on 
controller synthesis for resource-constrained problems modeled as Consumption Markov Decision Processes (CMDPs). The algorithms
are detailed in the work titled 'Qualitative Controller Synthesis for Consumption Markov Decision Processes' by 
František Blahoudek, Tomáš Brázdil, Petr Novotný, Melkior Ornik, Pranay Thangeda and Ufuk Topcu.

## Installation and Usage
Refer to the installation and usage section in the [documentation](https://fimdp.readthedocs.io/en/latest/install.html) for detailed instructions.

**Binder:**
Use this [link](https://mybinder.org/v2/gh/xblahoud/FiMDP/master) to access the interactive Jupter notebooks on the web without any installation.

**Docker:**
The docker image with FiMDP is published on Docker Hub at this [link](https://hub.docker.com/repository/docker/xblahoud/fimdp). 

**Local Installation:**
Refer to the [installation documentation](https://fimdp.readthedocs.io/en/latest/install.html).

## Example Environments
We provide a number of examples in Interactive Jupyter notebooks to explore the features of our tool, to 
analyze its performance, and also to validate the results presented in our paper. The two primary examples are 
the problems of an electric vehicle routing with limited capacity and a multi-agent grid world inspired by the 
Mars 2020 mission. The notebooks can be found in the `examples` subdirectory and their contents and described in
detail [here](https://fimdp.readthedocs.io/en/latest/examples.html).

<img src="https://raw.githubusercontent.com/xblahoud/FiMDP/master/docs/source/images/environments.png" alt="The two primary examples: electric vehicle routing and multi-agent grid world." align="center" height="259" width="570" >

## Contact
If you have any trouble with the installation, or have any questions, raise an issue or email [František Blahoudek](fandikb@gmail.com) or [Pranay Thangeda](contact@prny.me).



