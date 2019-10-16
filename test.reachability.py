from consMDP import ConsMDP
from reachability import PositiveReachability
from math import inf

def consMDP_double_flower(cap=32,path=3):
    m = ConsMDP()
    m.new_states(2)
    #m.add_action(1,{0:1},"a",1)
    #m.add_action(0,{1:1},"t",cap)

    for c in range(2,cap, 2):
        s = m.new_state(reload=True, label = f"{c}")
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
pr = PositiveReachability(m, set([2]), cap+2)

result = pr.get_positive_reachability()
expected = [3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3]

assert result == expected, ("get_positive_reachability() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")


pr = PositiveReachability(m, set([2]), cap)

result = pr.get_positive_reachability()
expected = [31, 30, 0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, 32, 31, 32, 31, 32, 31, 32, 31, 32, 31, 32, 31]