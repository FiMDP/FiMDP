# # Test computation of minimal capacity

from reachability_examples import ultimate
from fimdp.energy_solver import AS_REACH
from fimdp.mincap import bin_search
from fimdpenv.MarsEnv import MarsEnv
import matplotlib.pyplot as plt
from networkx.algorithms import tournament
#import MarsEnv
import numpy as np
import scipy.optimize
from scipy.optimize import linear_sum_assignment
import networkx as nx
import math
import multi_agent_codes
import fimdpenv.UUVEnv
from fimdpenv.env_multiagent import setup
from env_multiagent import visualize_allocation

from env_multiagent import create_env
setup()

agents_capacities = [200,200,200]
e = create_env(agents_capacities)
e.create_consmdp()
print(dir(e))
print(e.targets_all)
print(e.targets_list)
targets=e.targets_list
for item in targets:
    for item2 in targets:
        if not item==item2:
            result = bin_search(e, item, item2)
            print(result)

visualize_allocation(e)


result = bin_search(e, 345, 24)
# AttributeError: 'SynchronousMultiAgentEnv' object has no attribute 'num_states'

