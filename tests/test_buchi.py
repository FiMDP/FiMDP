#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# # Test computation of minimal initial loads for Büchi objective

from math import inf
from reachability_examples import ultimate, little_alsure


# ## Test case 1
# Simple computation of Büchi values on a non-trivial example where we need to go through reload states to obtain the optimal values.

# +
m, targets = ultimate()

result = m.get_Buchi(targets, 15)
expected = [6, inf, inf, 3, 0, 1, 10, inf, 4, inf, inf]
m.show()
# -

assert result == expected, ("get_Buchi() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_Buchi() in test_buchi file.")    

# ## Test case 2: insufficient capacity

# The same MDP, now with capacity 14. No initial load is enough.

result = m.get_Buchi(targets, 14)
expected = [inf] * m.num_states
m.show()

assert result == expected, ("get_Buchi() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_Buchi() in test_buchi file.")

# ## Test case 3: safe value of a reaload state is equal to capacity
# There was a bug where reloads with safe_values equal to capacity were removed as unusable.

m, T = little_alsure()
act = m.actions_for_state(3)
m.actions[act.next].distr = {0: 1}
m.show("M")

result = m.get_Buchi([1], 5)
expected = [2, 1, 2, 0]
m.show()

assert result == expected, ("get_Buchi() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n" +
    "Perhaps some reload should be 0 and is not")
print("Passed test 3 for get_Buchi() in test_buchi file.")
