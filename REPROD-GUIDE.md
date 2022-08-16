## Experiments reproducibility for AAAI 2023
### (Work in progress)
All experiment files are located in package **fipomdp/experiments**.
Included are also pickled files with pre-computed min Büchi levels, to reduce preprocessing time.

The experiments work in the following manner.
Firstly, the cpomdp is created and analysed by computing minimal levels (or pickled pre-analysed models are loaded instead).
This part is not parallelized.
Secondly multiple simulations are run in parallel, each seeded with a different random seed.

### Loggers
There is a global logger and a logger for each random seed per simulation of POMCP. The global logger is set in the **main** method.
In each experiment file, in method **log_experiment_with_seed**, you can specify the directory where the seeded logs are to be created (one log per seed may take up to 7 MB).
These logs are then used to collect data from the experiments. You can also specify the level of debugging in the main method,
though this is to be done with caution, because debug logs can produce over a GB of data.
Logging level is by default set to INFO.
###### Collecting results
There are two collecting scripts in package **fipomdp/experiments** - ***collect_data_script.py***, ***collect_from_sublogs_script.py***.
In case of shielded models, the first one will suffice, but when collecting data with the possibility of the agents death,
use ***sublogs_script***. 

***
***collect_data_script***

Takes one parameter, that is the path to the master log.

***collect_from_sublogs_script***

Takes two parameters, first is the path to directory with all sublogs, and second is a default reward to use upon agents death.

### Hyper-parameters and rollout functions
The top of each experiment file (first 40-60 lines) contains a section for modifying hyper parameters (e.g. exploration, rollout horizon, etc...).
There is also a section for setting the rollout function evaluation (see module ***rollout_functions.py*** in package **fipomdp**)

### Turning off the shield (Work in progress!)
To turn the shield off, in package **fipomdp** in file ***energy_solvers.py***, uncomment line 153. Then to reverse it just comment it back.
By setting minimal level for each action in each belief support state to theoretical negative infinity (for our experiments where no action cost exceeds 100, minimal level of -1000000 should suffice),
this effectively turns the shield off.

### Running an experiment
Now with everything setup, you can run the experiment (e.g. NYC_experiment.py) from linux CLI
```
python3 NYC_experiment.py > /dev/null
```
or (recommended) in the back
```
nohup python3 NYC_experiment.py > /dev/null &
```