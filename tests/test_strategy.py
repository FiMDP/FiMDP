# -*- coding: utf-8 -*-
# # Test the new interface for strategies
#
# ## Test Selection Rules
# Selection rules should work like Python `dict`. On top of that they provide function `select_action(energy)`. For printing purposes, we want the actions to be printed by their labels.
# 1. Test output for `print` and `__repr__`
# 2. Test dict interface
# 3. Test `select_action`
#   
#   1. correct
#   2. not feasible action
#   3. no action at all

from reachability_examples import basic
from fimdp.energy_solver import AS_REACH
from fimdp.strategy import SelectionRule

m, T = basic()

# Let's create some dummy selection rule

c = 2
rule = SelectionRule()
for a in m.actions_for_state(6):
    rule[c] = a
    c += 10

# The `__repr__` of `SelectionRule`s should show full information about the actions

rule

expected = '{\n  2 — 11: t,\n  12+: r\n}'
result = rule.__str__()
assert result == expected
print(result)
print("Passed test 1 for selection rules in file test_strategy.py")

# ### 2. Dictionary interface

rule2 = SelectionRule()
rule2[0] = rule[12]
rule2[3] = rule[2]
rule2

assert rule2[0].label == "r"
assert rule2.select_action(3).label == "t"
expected = {0: m.actions[9], 3: m.actions[8]}
assert expected == rule2
print("Passed test 2 for selection rules in fle test_strategy.py")

# ### 3. `select_action` 

from fimdp.strategy import NoFeasibleActionError

assert rule.select_action(2).label == 't'
assert rule.select_action(6).label == 't'
assert rule.select_action(11).label == 't'
assert rule.select_action(12).label == 'r'
assert rule.select_action(60).label == 'r'
print("Passed test 3 for selection rules (`select_action`) in file test_strategy.py")

try:
    rule.select_action(0)
    assert False
except NoFeasibleActionError:
    print("Passed test 4 for selection rules (`select_action`) in file test_strategy.py")

try:
    rule3 = SelectionRule()
    rule3.select_action(4)
    assert False
except NoFeasibleActionError:
    print("Passed test 5 for selection rules (`select_action`) in file test_strategy.py")

# ## Test CounterSelector
# 1. Test initialization (with an iterable, nothing)
# 2. Test update (correct and incorrect actions)
# 3. Test `select_action`

from fimdp.strategy import CounterSelector

# ### 1. Test initialization

selector = CounterSelector(m)
assert len(selector) == m.num_states

# Initialize with a list of dicts

# +
m.get_almostSureReachability(T)

s = list(m.energy_levels.get_strategy(AS_REACH))

selector = CounterSelector(m, s)
assert selector == s
selector
# -

print("Passed test 0 for CounterSelector in file test_strategy.py")

# ### 2. Update CounterSelector 
# Update selector should assign the correct tuples to correct underlying dicts. We will use some of the following actions:

selector = CounterSelector(m)
m.actions

selector.update(0, 2, m.actions[1])
selector.update(3, 12, m.actions[5])
selector.update(3, 15, m.actions[4])
selector.update(6, 15, m.actions[8])
selector.update(6, 10, m.actions[9])

selector

# In the following assert we test that:
#  * the selector contains the correct selection rules
#  * the `list` and `dict` representations should be equivalent to `CounterSelector` and `SelectionRule` (the order of values for state `6` is different in the expected list)

expected = [{2: m.actions[1]}, {}, {}, {12: m.actions[5], 15: m.actions[4]}, {}, {}, {10: m.actions[9], 15: m.actions[8]}, {}, {}]
assert selector == expected
print("Passed test 1 for CounterSelector (update) in file test_strategy.py")

# #### Test update with incorrect action
# If action that belongs to a state different from the given `state`, `ValueError` should be raised.

try:
    selector.update(1, 1, m.actions[8])
except ValueError as e:
    assert e.args[0] == "The action 6——t[6]——>{3: 0.5, 7: 0.5} is not valid for the state 1."
    print("Passed test 2 for CounterSelector (update with incorrect source) in file test_strategy.py")

# ### 3. Select action
# Selector should return the correct action for given `state` and `energy`, and raise `NoFeasibleActionError` in case no such action leads to satisfaction of the objective.

assert selector.select_action(0, 10) == m.actions[1]
assert selector.select_action(0, 2) == m.actions[1]
assert selector.select_action(6, 10) == m.actions[9]
print("Passed test 3 for CounterSelector (select_action) in file test_strategy.py")

try:
    selector.select_action(6, 9)
    assert False
except NoFeasibleActionError:
    print("Passed test 4 for CounterSelector (select_action) in file test_strategy.py")

try:
    selector.select_action(2, 16)
    assert False
except NoFeasibleActionError:
    print("Passed test 5 for CounterSelector (select_action) in file test_strategy.py")

# ## Test Strategy interface
# We first create a simple strategy that always chooses the first action for the current state.

from fimdp.strategy import Strategy, WrongCallOrderError
class FirstStrategy(Strategy):
    def _next_action(self):
        actions = self.mdp.actions
        a_id = self.mdp.actions_for_state(self._current_state).next
        return actions[a_id]


# +
s = FirstStrategy(m, 0)

s.next_action()
s.update_state(1)
s.next_action()
s.update_state(0)
s.next_action()
s.update_state(1)
result = s.next_action()
expected = m.actions[2]
assert result == expected
print("Passed test 1 for Strategy in file test_strategy.py")
# -

s.reset(0)
s.next_action()
s.update_state(1)
s.next_action()
s.update_state(0)
s.next_action()
s.update_state(1)
result = s.next_action()
expected = m.actions[2]
assert result == expected
print("Passed test 2 for Strategy in file test_strategy.py")

# Now let's test the `next_action(outcome)` calls

# +
s = FirstStrategy(m)

s.next_action(0)
result = s.next_action(1)
assert result == expected
print("Passed test 3 for Strategy in file test_strategy.py")
# -

# #### Test checks for order of calls and maintaining history

try:
    s = FirstStrategy(m, 0)
    s.next_action(0)
    assert False
except WrongCallOrderError:
    print("Passed test 4 for Strategy in file test_strategy.py")

try:
    s = FirstStrategy(m, 0)
    s.next_action()
    s.next_action()
    assert False
except WrongCallOrderError:
    print("Passed test 5 for Strategy in file test_strategy.py")

try:
    s = FirstStrategy(m)
    s.next_action(0)
    s.update_state(1)
    s.next_action(1)
    assert False
except WrongCallOrderError:
    print("Passed test 6 for Strategy in file test_strategy.py")

# #### Test outcome check

try:
    s = FirstStrategy(m, 0)
    s.next_action()
    s.update_state(3)
    assert False
except ValueError:
    print("Passed test 7 for Strategy in file test_strategy.py")

# # Test CounterStrategy

from fimdp.strategy import CounterStrategy

# +
m.get_almostSureReachability(T, 30)
selector = m.energy_levels.get_strategy(AS_REACH)
s = CounterStrategy(m, selector=selector,
                    capacity=30, 
                    init_energy=15, init_state=6)

s.next_action()
s.update_state(7)
assert s.energy == 14
s.next_action()
s.update_state(6)
assert s.energy == 27
s.next_action()
s.update_state(3)
assert s.energy == 21
s.next_action()
s.next_action(6)
s.next_action(7)
assert s.energy == 10
s.next_action(6)
s.next_action(3)
s.next_action(4)
s.next_action(5)
assert s.energy == 10
print("Passed test 1 for CounterStrategy in file strategy.py")
# -

s.reset(6, 15)
s.next_action()
s.update_state(7)
assert s.energy == 14
s.next_action()
s.update_state(6)
assert s.energy == 27
s.next_action()
s.update_state(3)
assert s.energy == 21
s.next_action()
s.next_action(6)
s.next_action(7)
assert s.energy == 10
s.next_action(6)
s.next_action(3)
s.next_action(4)
s.next_action(5)
assert s.energy == 10
print("Passed test 2 for CounterStrategy in file strategy.py")

# Test start in a loosing reagion

s = CounterStrategy(m, selector=selector, capacity=30, init_energy=15, init_state=1)
try:
    s.next_action()
    assert False
except NoFeasibleActionError:
    print("Passed test 3 for CounterStrategy in file strategy.py")
