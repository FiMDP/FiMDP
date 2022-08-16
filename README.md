# FiPOMDP - Fuel in Partially Observable Markov Decision Processes

##### Python package for synthesizing resource-safe strategies on Resource-constrained POMDPs
This project extends [FiMDP] representation of Consumption MDP by adding partial observability, thus creating the Consumption POMDP model.
On this model, strategies are estimated step-by-step firstly by computing a Büchi-safe shield and recommended actions are subsequently produced by the POMCP algorithm
(limiting actions of the agent based on the shield) tuned for the consumption model.

The shielding itself is done by reducing the qualitative analysis of a Resource-constrained POMDP to a problem of analysing an extension of known belief support construction (more details in the submission for AAAI 2023).
FiPOMDP implements algorithms for producing these constructions, computes minimal energy levels (implemented in [FiMDP]), and from those levels produces a shield - a minimal energy value per action for each belief (belief support).

The package includes a POMCP processor for POMDP (and experimental variations for different environments)

## Installation (regarding experiments)
You can install all required dependencies for running experiments with
```
pip install -r requirements.txt
```

## Demo (Work in progress)
In directory fipomdp/demo is also included a demo notebook showing how to create a simple CPOMDP, and create a shield via qualitative analysis.
For more information about FiMDP, computing minimal levels and creating Consumption MDPs without partial observability, look at [FiMDP README] file.

## Experiments for AAAI 2023
The experiments we performed use environments from [FiMDPEnv] modified for partial observability.
Since there are many slight variations to configurations in experiments, a small tutorial how to launch them and collect results from them is included.
The experiments are reproducible, specified more exactly in the [Experiment reproducibility guide].

[FiMDPEnv]: https://github.com/FiMDP/FiMDPEnv
[FiMDP]: https://github.com/FiMDP/FiMDP
[FiMDP README]: https://github.com/xbrlej/FiPOMDP/blob/master/FiMDP-README.md
[Experiment reproducibility guide]: https://github.com/xbrlej/FiPOMDP/blob/master/REPROD-GUIDE.md