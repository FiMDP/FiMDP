#!/usr/bin/env python3

from fimdp.labeledConsMDP import LCMDP
from math import inf

# Test simple assigment of APs
m = LCMDP(AP=["a","b"])

m.new_state(label={0})
m.new_state(label={1})
m.new_state(label={0,1})
m.new_state(label=set())
m.new_state()

assert m.state_labels[0] == {0}
assert m.state_labels[1] == {1}
assert m.state_labels[2] == {0,1}
assert m.state_labels[3] == set()
assert m.state_labels[4] == set()

print("Passed test 1 for LCMDP.")

# Test assigment of non-existent AP
try:
    m.new_state(label={2})
except ValueError:
    pass
else:
    raise AssertionError("Invalid AP was given, but not reported!")
print("Passed test 2 for LCMDP (non-existent AP).")

# Test AP & names at the same time
m = LCMDP(AP=["a","b"])
m.new_state(name="s0")
m.new_state(name="s1", label={0,1})

assert m.state_labels[0] == set()
assert m.state_labels[1] == {0,1}
assert m.state_with_name("s1") == 1

m.new_states(3,labels=[{0},{1},{0,1}])

assert m.state_labels[2] == {0}
assert m.state_labels[3] == {1}
assert m.state_labels[4] == {0,1}

# Test assigment of non-existent AP
try:
    m.new_states(2,labels=[{2},{0}])
except ValueError:
    pass
else:
    raise AssertionError("Invalid AP was given, but not reported!")

print("Passed test 3 for LCMDP (labels & names).")

# states_with_label
m = LCMDP(AP=["a","b","c"])
count = 100
a_labels = [{0} if i % 2 == 0 else set() for i in range(count)]
b_labels = [{1} if i % 3 == 1 else set() for i in range(count)]
c_labels = [{2} if i % 5 == 0 else set() for i in range(count)]

labels = [a_labels[i].union(b_labels[i]).union(c_labels[i]) for i in range(count)]
m.new_states(count, labels=labels)

assert m.states_with_label({0,2}) == [0,20,30,50,60,80,90]
print("Passed test 4 for LCMDP (states_with_label).")

# Check that algorithms work also on LCMDP
m = LCMDP(["a"])
m.new_states(11, labels=[{0}]*11)
for r in [2, 4, 9]:
    m.set_reload(r)
T = {7, 8, 10}

m.add_action(0, {1: .5, 2: .5}, "a", 1)
m.add_action(0, {3: .5, 4: .5}, "t", 3)
m.add_action(1, {2: 1}, "", 1)
m.add_action(2, {1: 1}, "", 1)

m.add_action(3, {2: .5, 7: .5}, "p", 1)
m.add_action(3, {5: 1}, "r", 2)
m.add_action(3, {6: 1}, "a", 3)

m.add_action(4, {5: 1}, "", 1)
m.add_action(5, {4: 1}, "r", 1)
m.add_action(5, {3: 1}, "t", 1)

m.add_action(6, {7: .5, 10: .5}, "a", 3)
m.add_action(6, {3: .5, 8: .5}, "B", 6)

m.add_action(7, {9: 1}, "", 1)
m.add_action(9, {9: 1}, "", 1)
m.add_action(10, {9: 1}, "", 1)

m.add_action(8, {5: 1}, "r", 3)

targets = T
result = m.get_Buchi(targets, 15)
expected = [6, inf, inf, 3, 0, 1, 10, inf, 4, inf, inf]

assert result == expected, ("get_Buchi() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")

# WIth cap < 15, we get all infs
result = m.get_Buchi(targets, 14)
expected = [inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf]

assert result == expected, ("get_Buchi() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")

print("Passed test 5 for LCMDP (algo).")