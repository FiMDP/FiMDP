from consMDP import ConsMDP
from math import inf
from reachability_examples import ultimate

m, targets = ultimate()

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


# Test case when reload's safe_value = cap
from reachability_examples import little_alsure
m, T = little_alsure()
act = m.actions_for_state(3)
m.actions[act.next].distr = {0: 1}

result = m.get_Buchi([1], 5)
expected = [2, 1, 2, 0]

assert result == expected, ("get_Buchi() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n" +
    "Perhaps some reload should be 0 and is not")
