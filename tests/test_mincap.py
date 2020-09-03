# # Test computation of minimal capacity

from reachability_examples import ultimate
from fimdp.energy_solver import AS_REACH
from fimdp.mincap import bin_search
from fimdpenv.MarsEnv import MarsEnv

#import MarsEnv
import numpy as np
import scipy.optimize
from scipy.optimize import linear_sum_assignment
# In the following example, the minimal capacity is 15 for Buchi objective defined by the blue states.

def get_assignment(m,T,env):
    """

    :param m: FiMDP model
    :param T: set of targets: which is a proxy here
    :param env: FiMDP env
    :return:
    assignment_dict: Assigns a min cost target for each target
    """
    #Initialize the cost array
    num_targets=len(T)
    cost_array = np.zeros((num_targets, num_targets))
    #Two dicts that map numpy array indices to targets
    numpy_index_to_agent_index_dict = dict()
    agent_index_to_numpy_index_dict = dict()

    #Generate dicts
    i = 0
    for item in T:
        numpy_index_to_agent_index_dict[i] = item
        agent_index_to_numpy_index_dict[item] = i

        i = i + 1
    #Randomly generate costs from each target to another target for now
    i = 0
    for item in T:
        j = 0
        for item2 in T:
            try:
                # result = bin_search(m, item, item2,starting_capacity=20)
                cost_array[i, j] = np.random.uniform(0, 1)
                # print(result,item,item2)
            except:
                pass
            j = j + 1
        i = i + 1
    #Compute assignment
    row_ind, col_ind = linear_sum_assignment(cost_array)
    #Gather min_cost assignments for each target
    assignment_dict = dict()
    for item in T:
        index = agent_index_to_numpy_index_dict[item]
        assignment_dict[item] = numpy_index_to_agent_index_dict[col_ind[index]]
    #return assignment
    return assignment_dict
m, T = ultimate()
m.get_Buchi(T, capacity=15)
m

m.get_Buchi(T, capacity=14)
m

# +
result = bin_search(m, 0, T)
expected = 15

assert result == expected, (f"The minimal capacity should be {expected}, not {result}.")
print("Passed test 1 for bin_search() in test_mincap.py file.")
# -

# ### Capacity too small
# If the starting capacity is not enough, an exception should be raised.

try:
    result = bin_search(m, 0, T, starting_capacity=14)
except ValueError as e:
    assert e.args[0] == "No capacity <= 14 is enough."
print("Passed test 2 for bin_search() in test_mincap.py file.")

# ### With maximal initial load

# +
result = bin_search(m, 0, T, max_starting_load=8)
expected = 15

assert result == expected, (f"The minimal capacity should be {expected}, not {result}.")
print("Passed test 3 for bin_search() in test_mincap.py file.")
# -

try:
    result = bin_search(m, 0, T, max_starting_load=5)
except ValueError as e:
    assert e.args[0] == "No capacity <= 100 is enough."
    print("Passed test 4 for bin_search() in test_mincap.py file.")

# ## Almost-sure Reachability
# For almost-sure reachability, the minimum capacity needed from state 0 is 8

m.get_almostSureReachability(T, capacity=9)
m

m.get_almostSureReachability(T, capacity=8)
m

# +
result = bin_search(m, 0, T, objective=AS_REACH)
expected = 9

assert result == expected, (f"The minimal capacity should be {expected}, not {result}.")
print("Passed test 5 for bin_search() in test_mincap.py file.")
# -

# ### Different initial state

# +
result = bin_search(m, 3, T, objective=AS_REACH)
expected = 7

assert result == expected, (f"The minimal capacity should be {expected}, not {result}.")
print("Passed test 6 for bin_search() in test_mincap.py file.")

env = MarsEnv(grid_size=5, agent_capacity=20, agent_actioncost=1, agent_staycost=1)
m, T = env.get_mdp_targets()
assignment=get_assignment(m,T,env)
print(assignment)