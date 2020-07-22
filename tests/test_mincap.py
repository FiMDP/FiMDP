# # Test computation of minimal capacity

from reachability_examples import ultimate
from fimdp.energy_solver import AS_REACH
from fimdp.mincap import bin_search

# In the following example, the minimal capacity is 15 for Buchi objective defined by the blue states.

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
