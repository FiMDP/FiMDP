#!/usr/bin/env python3

import sys; sys.path.insert(0, '..')
from reachability_examples import basic, ultimate
from fimdp.energy_solver import *

m, T = ultimate()
solver = EnergySolver(m, 30, T)
safe = solver.get_strategy(SAFE)
pr = solver.get_strategy(POS_REACH)
asr = solver.get_strategy(AS_REACH)
buchi = solver.get_strategy(BUCHI)

safe_expected = [
    {2: 'a'},
    {1: ''},
    {2: ''},
    {2: 'p'},
    {2: ''},
    {1: 'r'},
    {4: 'a'},
    {1: ''},
    {4: 'r'},
    {1: ''},
    {1: ''}
]

pr_expected = [
    {5: 't'},
    {},
    {},
    {2: 'p'},
    {0: ''},
    {3: 't', 1: 'r'},
    {4: 'a'},
    {1: ''},
    {4: 'r'},
    {},
    {1: ''}
]

asr_expected = [
    {10: 't', 6: 't'},
    {},
    {},
    {7: 'a', 3: 'r'},
    {0: ''},
    {8: 't', 1: 'r'},
    {4: 'a'},
    {1: ''},
    {4: 'r'},
    {},
    {1: ''}
]

buchi_expected = [
    {16: 't', 6: 't'},
    {},
    {},
    {13: 'a', 3: 'r'},
    {0: ''},
    {14: 't', 1: 'r'},
    {10: 'B'},
    {},
    {4: 'r'},
    {},
    {}
]

assert safe == safe_expected, ("Wrong strategy for safe\n"
    f"  expected: {safe_expected}\n  returns:  {safe}\n")
print("Passed test for solver.get_strategy(SAFE) in test_strategy file.")

assert pr == pr_expected, ("Wrong strategy for safe\n"
    f"  expected: {pr_expected}\n  returns:  {pr}\n")
print("Passed test for solver.get_strategy(POS_REACH) in test_strategy file.")

assert asr == asr_expected, ("Wrong strategy for safe\n"
    f"  expected: {asr_expected}\n  returns:  {asr}\n")
print("Passed test for solver.get_strategy(AS_REACH) in test_strategy file.")

assert buchi == buchi_expected, ("Wrong strategy for safe\n"
    f"  expected: {buchi_expected}\n  returns:  {buchi}\n")
print("Passed test for solver.get_strategy(BUCHI) in test_strategy file.")
