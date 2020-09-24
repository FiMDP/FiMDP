#!/usr/bin/env python3
"""
# Test reachability objectives
"""

import fimdp
from fimdp.core import ConsMDP
from fimdp.energy_solvers import BasicES
from math import inf
from reachability_examples import basic, little_alsure, little_alsure2


###############################################################################
# ## Double flower example: test case 1 & 2
# The almost worst-case for reachability run time. The capacity used for generating the example is not enough (it is in fact a target value for the states connecting the two flowers). 

def consMDP_double_flower(cap=32,path=3):
    m = ConsMDP()
    m.new_states(2)
    #m.add_action(1,{0:1},"a",1)
    #m.add_action(0,{1:1},"t",cap)

    for c in range(2,cap, 2):
        s = m.new_state(reload=True, name=f"{c}")
        h = (c//2) % 2
        m.add_action(h,{s:1},f"{s}",cap-c)
        m.add_action(s,{h:1},"a",c-1)
        
    prev_o = 1
    prev_e = 0
    for p in range(path):
        curr_o = m.new_state()
        curr_e = m.new_state()

        m.add_action(prev_o,{curr_o:1},"p",0)
        m.add_action(prev_e,{curr_e:1},"p",0)
        
        prev_o = curr_o
        prev_e = curr_e
        
    m.add_action(prev_o,{0:1},"p",1)
    m.add_action(prev_e,{1:1},"p",1)
    
    return m

fimdp.dot.dotpr = "neato"

""
cap = 32 # We have cap/2 reload states, cap/4 in each flower
path = 6
m = consMDP_double_flower(cap, path)

solver = BasicES(m, cap=cap + 2, targets=[2])
result = solver.get_positiveReachability()
expected = [3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3]
solver

""
assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_positive_reachability() in test_reachability file.")

""
solver = BasicES(m, cap=cap, targets=[2])
result = solver.get_positiveReachability()
expected = [31, 30, 0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, 32, 31, 32, 31, 32, 31, 32, 31, 32, 31, 32, 31]
solver

""
assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_positive_reachability() in test_reachability file.")

###############################################################################
# ## Simple example: test cases 3 & 4

fimdp.dot.dotpr = "dot"
m = ConsMDP()
m.new_states(13)
for sid in [0,3,4,9,11]:
    m.set_reload(sid)

m.add_action(1, {0:.5, 2: .25, 12: .25}, "a", 1)
m.add_action(2, {4:1}, "a", 2)
m.add_action(12, {3:1}, "a", 1)
m.add_action(3, {3:.5, 4: .5}, "a", 1)
m.add_action(4, {1:1}, "a", 0)
m.add_action(7, {3:1}, "a", 1)
m.add_action(7, {6:1}, "b", 1)
m.add_action(6, {4:.5, 5:.5}, "a", 5)
m.add_action(5, {1:1}, "a", 6)
m.add_action(8, {9:1}, "a", 1)
m.add_action(8, {1:1}, "b", 3)
m.add_action(10, {1:.5, 11:.5}, "a", 2)
m.add_action(0, {0:1}, "r", 0)
m.add_action(9, {9:1}, "r", 0)
m.add_action(11, {11:1}, "a", 1)
m.add_action(4, {9:.5, 5:.5}, "t", 7)

T = set([9])

""
solver = BasicES(m, cap=16, targets=T)
result = solver.get_positiveReachability()
expected = [inf, 3, 2, 0, 0, 9, 14, 1, 1, 0, 5, inf, 1]
solver

""
assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 3 for get_positive_reachability() in test_reachability file.")

""
# Reduce the capacity so that we can't be sure to survive from 4.
solver = BasicES(m, cap=15, targets=T)
result = solver.get_positiveReachability()
expected = [inf, inf, inf, inf, inf, inf, inf, inf, 1, 0, inf, inf, inf]
solver

""
assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for get_positive_reachability() in test_reachability file.")

###############################################################################
# ## Basic example for positive reachability (test case 5)
# The path from state 5 leads via reload.

m, targets = basic()

solver = BasicES(m, cap=22, targets=targets)
result = solver.get_positiveReachability()
expected = [inf, inf, 2, 3, 3, 2, 1, 0, 7]
solver

""
assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 5 for get_positive_reachability() in test_reachability file.")

###############################################################################
# ## Almost sure reachability
# Positive and almost sure reachability values differs in the following example. The almost sure values should be non-zero in state 0.

m, targets = little_alsure()

solver = BasicES(m, 10, targets)
result_pos = solver.get_positiveReachability()
expected_pos = [2, 1, 2, inf]

result_as = solver.get_almostSureReachability()
expected_as = [4, 1, 2, inf]

solver

""
assert result_pos == expected_pos, ("get_positiveReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected_pos}\n  returns:  {result_pos}\n")
print("Passed test 6 for get_positive_reachability() in test_reachability file.")

""
assert result_as == expected_as, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected_as}\n  returns:  {result_as}\n")
print("Passed test 1 for get_almostSureReachability() in test_reachability file.")

###############################################################################
# ## Basic example with almost-sure reachability
# With capacity 22, the almost-sure and positive reachability differ only in state 3. For 20, however, the reload state 7 becomes unsuitable for almost-sure objective and this change propagates further.

m, targets = basic()

solver = BasicES(m, 22, targets)
solver.get_positiveReachability()
result = solver.get_almostSureReachability()
expected = [inf, inf, 2, 13, 3, 2, 1, 0, 7]
solver
""
assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_almostSureReachability() in test_reachability file.")

""
# For 20 the reload 7 get's disabled
solver = BasicES(m, 20, targets)
solver.get_positiveReachability()
result = solver.get_almostSureReachability()
expected = [inf, inf, 2, inf, 3, 2, inf, inf, inf]
solver

""
assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 3 for get_almostSureReachability() in test_reachability file.")

###########################
# ## Little example
# almost sure has to be 5 in the newly added state 4.

m, targets = little_alsure2()

solver = BasicES(m, 10, targets)
solver.get_positiveReachability()
result = solver.get_almostSureReachability()
expected = [4, 1, 2, inf, 5]
solver

""
assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for get_almostSureReachability() in test_reachability file.")
