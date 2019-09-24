import consMDP
from math import inf
from safety import minInitCons

m = consMDP.ConsMDP()
m.new_states(13)
for sid in [0,3,4,9,11]:
    m.set_reload(sid)

m.add_action(1, {0:.5, 2: .25, 12: .25}, "a", 1)
m.add_action(2, {4:1}, "a", 2)
m.add_action(12, {3:1}, "a", 1)
m.add_action(3, {3:.5, 4: .5}, "a", 0)
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

MI = minInitCons(m)

result   = MI.get_values()
expected = [0, 3, 2, 0, 3, 9, 14, 1, 1, 0, 5, 1, 1]

assert result == expected, ("minInitCons.get_values() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")


m.unset_reload(11)

result = MI.get_values(recompute=True)
expected = [0, 3, 2, 0, 3, 9, 14, 1, 1, 0, inf, inf, 1]

assert result == expected, ("minInitCons.get_values() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")