#!/usr/bin/env python3

import sys; sys.path.insert(0, '..')
from fimdp import consMDP
from consMDP import ConsMDP
from math import inf
from reachability_examples import basic, little_alsure, little_alsure2

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

cap = 32 # We have cap/2 reload states, cap/4 in each flower
path = 6
m = consMDP_double_flower(cap, path)

result = m.get_positiveReachability(set([2]), cap+2)
expected = [3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3]

assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_positive_reachability() in test_reachability file.")

result = m.get_positiveReachability(set([2]), cap)
expected = [31, 30, 0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, 32, 31, 32, 31, 32, 31, 32, 31, 32, 31, 32, 31]

assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_positive_reachability() in test_reachability file.")


## kuchera_example

m = consMDP.ConsMDP()
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

T = set([9])
targets = [True if s in T else False for s in range(m.num_states)]
m.add_action(4, {9:.5, 5:.5}, "t", 7)

result = m.get_positiveReachability(T, 16)
expected = [inf, 3, 2, 0, 0, 9, 14, 1, 1, 0, 5, inf, 1]

assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 3 for get_positive_reachability() in test_reachability file.")

# Reduce the capacity so that we can't be sure to survive from 4.
result = m.get_positiveReachability(T, 15)
expected = [inf, inf, inf, inf, inf, inf, inf, inf, 1, 0, inf, inf, inf]

assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for get_positive_reachability() in test_reachability file.")


m, targets = basic()

result = m.get_positiveReachability(targets, 22)
expected = [inf, inf, 2, 3, 3, 2, 1, 0, 7]

assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 5 for get_positive_reachability() in test_reachability file.")


### Almost sure reachability
# almost sure different from positive
# almost sure non-zero in state 0

m, targets = little_alsure()

result = m.get_positiveReachability(targets, 10)
expected = [2, 1, 2, inf]

assert result == expected, ("get_positiveReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 6 for get_positive_reachability() in test_reachability file.")


result = m.get_almostSureReachability(targets, 10)
expected = [4, 1, 2, inf]

assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_almostSureReachability() in test_reachability file.")

###########################
m, targets = basic()

result = m.get_almostSureReachability(targets, 22)
expected = [inf, inf, 2, 13, 3, 2, 1, 0, 7]

assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_almostSureReachability() in test_reachability file.")

# For 20 the reload 7 get's disabled
result = m.get_almostSureReachability(targets, 20)
expected = [inf, inf, 2, inf, 3, 2, inf, inf, inf]

assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 3 for get_almostSureReachability() in test_reachability file.")

###########################
# almost sure has to be 5 in the newly added state 4.

m, targets = little_alsure2()

result = m.get_almostSureReachability(targets, 10)
expected = [4, 1, 2, inf, 5]

assert result == expected, ("get_almostSureReachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for get_almostSureReachability() in test_reachability file.")
