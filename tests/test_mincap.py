# # Test computation of minimal capacity

from reachability_examples import ultimate
from fimdp.energy_solvers import BasicES
from fimdp.objectives import AS_REACH, BUCHI
from fimdp.mincap_solvers import bin_search

# In the following example, the minimal capacity is 15 for Buchi objective defined by the blue states.

m, T = ultimate()
solver15 = BasicES(m, 15, T)
solver15.get_min_levels(BUCHI)
solver15

solver14 = BasicES(m, 14, T)
solver14.get_min_levels(BUCHI)
solver14

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

solver9 = BasicES(m, 9, T)
solver9.get_min_levels(AS_REACH)
solver9

solver8 = BasicES(m, 8, T)
solver8.get_min_levels(AS_REACH)
solver8

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
