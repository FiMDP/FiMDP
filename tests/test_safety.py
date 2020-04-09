#!/usr/bin/env python3

import sys; sys.path.insert(0, '..')
from cmdp import consMDP
from math import inf
from cmdp.energy_solver import EnergySolver, EnergyLevels_least
from sys import stderr

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

MI = EnergySolver(m)

result   = MI.get_minInitCons()
expected = [0, 3, 2, 1, 3, 9, 14, 1, 1, 0, 5, 1, 1]

assert result == expected, ("EnergySolver.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for EnergySolver.get_minInitCons() in test_safety file.")

m.unset_reload(11)

result = MI.get_minInitCons(recompute=True)
expected = [0, 3, 2, 1, 3, 9, 14, 1, 1, 0, inf, inf, 1]

assert result == expected, ("EnergySolver.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for EnergySolver.get_minInitCons() in test_safety file.")

## Test EnergySolver with capacity
MI.cap=14
result = MI.get_minInitCons(recompute=True)
result2 = m.get_minInitCons(14)
expected = [0, 3, 2, 1, 3, 9, 14, 1, 1, 0, inf, inf, 1]

assert result == result2, ("result and result2 should be the same\n" +
    f"  result  : {result}\n" +
    f"  result2 : {result2}\n")
print("Passed test 3 for EnergySolver.get_minInitCons() in test_safety file.")

assert result == expected, ("EnergySolver.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for EnergySolver.get_minInitCons() in test_safety file.")

result = m.get_minInitCons(capacity=13)
expected = [0, 3, 2, 1, 3, 9, inf, 1, 1, 0, inf, inf, 1]

assert result == expected, ("EnergySolver get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 5 for EnergySolver.get_minInitCons() in test_safety file.")

## Test safe reloads:
result = m.get_safe(14)
expected = [0, 3, 2, 0, 0, 9, 14, 1, 1, 0, inf, inf, 1]

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = EnergyLevels_least(m, 14)
result = m.get_safe(14)
assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_safe() in test_safety file.")

# Change the consumption on the action of st. 3
# This makes state 3 an useless reload
a = next(m.actions_for_state(3))
a.cons = 15
m.structure_change()

result = m.get_safe(14)
expected = [0, inf, inf, inf, inf, inf, inf, inf, 1, 0, inf, inf, inf]

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 3 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = EnergyLevels_least(m, 14)
result = m.get_safe(14)
assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for EnergyLevels_least() in test_safety file.")

### Reloads are not safe with EnergySolver.= ∞ even with cap = ∞
m = consMDP.ConsMDP()
m.new_states(4)
m.set_reload(2)
m.set_reload(0)
m.add_action(0, {0:1}, "", 1)
m.add_action(1, {0:1}, "a", 1000)
m.add_action(1, {2:1}, "b", 1)
m.add_action(3, {3:1}, "r", 1010)
m.add_action(1, {3:1}, "r", 1)
m.add_action(2, {3:1}, "r", 1)

result = m.get_safe()
expected = [0, 1000, inf, inf]

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = EnergyLevels_least(m)
result = m.get_safe()
assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 5 for get_safe() in test_safety file.")

## Example of incorrectness of the least fixpoint algorithm bounded by $|S|$ steps

m = consMDP.ConsMDP()
m.new_state(True)
m.new_states(2)
m.add_action(0, {0:1}, "", 0)
m.add_action(1, {0:1}, "a", 1000)
m.add_action(1, {2:1}, "b", 1)
m.add_action(2, {1:1}, "b", 1)
MI = EnergySolver(m)

result = MI.get_minInitCons()
expected = [0,1000,1001]

assert result == expected, ("EnergySolver.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 6 for EnergySolver.get_minInitCons() in test_safety file.")

## Example of the incorrectness of bounding SafeReloads by |S| iterations

m = consMDP.ConsMDP()
m.new_state(True)
m.new_states(2)
m.new_state(True)
m.add_action(0, {0:1}, "", 1)
m.add_action(1, {0:1}, "a", 1000)
m.add_action(1, {2:1}, "b", 1)
m.add_action(2, {1:1}, "b", 1)
m.add_action(3, {3:1}, "r", 1010)
m.add_action(1, {3:1}, "r", 1)
m.add_action(2, {3:1}, "r", 1)

result = m.get_safe(1005)
expected = [0, 1000, 1001, inf]

assert result == expected, ("EnergyLevels.get_safe() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 6 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = EnergyLevels_least(m, 1005)
result = m.get_safe()
assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 7 for get_safe() in test_safety file.")
