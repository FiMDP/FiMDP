"""
Objectives that can be used in FiMDP.

 * **MIN_INIT_CONS** stands for _minimal initial consumption_. It is the
   minimal energy needed to surely reach some reloading state from each state.
 * **SAFE** stands for _survival_. A SAFE strategy σ guarantees that all
   plays according to σ will never deplete energy with given capacity. *
 **POS_REACH** stands for _positive reachability_. This subsumes survival and
   moreover, there the probability to reach the specified target set is larger
   than 0.
 **AS_REACH** stands for _almost-sure reachability_. Similar to positive
   reachability, but here the probability is equal to 1.
 **BUCHI** stands for _almost-sure Büchi_. The probability that the target
   set will be visited infinitely often is equal to 1.
"""
MIN_INIT_CONS = 0
SAFE = 1
POS_REACH = 2
AS_REACH = 3
BUCHI = 4

# For energy solvers
max_objective = BUCHI
_HELPER_AS_REACH = max_objective + 1
_HELPER_BUCHI = _HELPER_AS_REACH + 1
_OBJ_COUNT = _HELPER_BUCHI + 1