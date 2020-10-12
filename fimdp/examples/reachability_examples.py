# -*- coding: utf-8 -*-
from .. import dot
from ..core import ConsMDP
from ..distribution import uniform


# ## Almost sure reachability example
#  * it should distinguish between positive and almost-sure reachability:
#    - target that does not reach any other target
#    - target reachable by an action that can lead to a dead-end for a low cost (and maybe has another way to reach the target surely for a high cost) 
#  * the good path goes via at least one reload
#    - the reload should be enabled by the same state
# 
# Capacity should be 25
def basic():
    m = ConsMDP(layout="neato")

    m.new_states(9)
    for s in [0, 7]:
        m.set_reload(s)

    m.add_action(0, {1:1}, "", 1)
    m.add_action(1, {0:1}, "", 1)
    m.add_action(2, {1:1}, "", 1)
    m.add_action(3, {2:.5, 1:.5}, "", 1)
    m.add_action(3, {4:.5, 6:.5},"t", 10)
    m.add_action(4, {5:1}, "t", 1)
    m.add_action(5, {6:1}, "r", 1)
    m.add_action(6, {3:.5, 7:.5}, "t", 6)
    m.add_action(6, {7:1}, "r", 1)
    m.add_action(7, {3:1}, "", 20)
    m.add_action(7, {6:1}, "t", 3)
    m.add_action(8, {7:.5, 2:.5}, "", 5)

    targets = set([2,5])
    
    return m, targets


def explicit():
    mdp = ConsMDP(layout="dot")
    mdp.new_states(5)
    mdp.set_reload(4)
    mdp.add_action(0, uniform([1,2]), "α", 1)
    mdp.add_action(0, uniform([2,3]), "β", 2)
    mdp.add_action(1, uniform([3]), "r", 1)
    mdp.add_action(2, uniform([3]), "r", 1)
    mdp.add_action(3, uniform([0, 4]), "s", 1)
    mdp.add_action(3, uniform([4]), "r", 2)
    mdp.add_action(4, uniform([0]), "i", 2)
    T = [1,2]
    return mdp, T


def goal_leaning():
    m = ConsMDP(layout="dot")
    m.new_states(3)
    for r in [0, 2]:
        m.set_reload(r)
    m.add_action(0, {1:.5, 0:.5}, "top", 1)
    m.add_action(0,{1:.7, 0:.3},"bottom",1)
    m.add_action(1,{2:1}, "r", 1)
    m.add_action(2,{2:1}, "r", 2)

    targets=set([2])
    return m, targets


def goal_leaning_2():
    m = ConsMDP(layout="dot")
    m.new_states(4)
    for r in [0, 2]:
        m.set_reload(r)
    m.add_action(0, {1:.5, 3:.5}, "sure", 1)
    m.add_action(0,{1:.7, 0:.3},"cycle",1)
    m.add_action(1,{2:1}, "r", 1)
    m.add_action(3,{2:1}, "r", 1)
    m.add_action(2,{2:1}, "r", 3)

    targets=set([2])
    return m, targets


def little_alsure():
    m = ConsMDP(layout="dot")
    m.new_states(4)
    for r in [3]:
        m.set_reload(r)
    m.add_action(0, {1:.5, 2:.5}, "t", 2)
    m.add_action(1,{3:1}, "r", 1)
    m.add_action(2,{3:1}, "r", 2)
    m.add_action(3,{3:1}, "r", 3)
    m.add_action(0,{1:.5, 3:.5},"pos",1)

    targets=set([1,2])
    return m, targets

def little_alsure2():
    m, T = little_alsure()
    m.new_state()
    m.add_action(4, {0:.5, 2:.5}, "", 1)
    return m, T

def product_example():
    mdp = ConsMDP(layout="dot")
    mdp.new_states(4)
    mdp.set_reload(3)
    mdp.add_action(0, uniform([1,2]), "α", 3)
    mdp.add_action(0, uniform([2,3]), "β", 1)
    mdp.add_action(1, uniform([3]), "r", 3)
    mdp.add_action(2, uniform([3]), "r", 1)
    mdp.add_action(3, uniform([0]), "s", 3)
    return mdp, {1, 2}

def two_step():
    two_step = ConsMDP(layout="neato")
    two_step.new_states(4)
    two_step.set_reload(1)
    two_step.set_reload(3)
   
    two_step.add_action(0, {1: .99, 3: .01}, "direct", 1)
    two_step.add_action(1, {0: 1}, "", 1)
    two_step.add_action(0, {2: 1}, "long", 1)
    two_step.add_action(2, {3: 1}, "long", 1)
    two_step.add_action(3, {3: 1}, "rel", 1);

    return two_step, {3}

def ultimate():
    m = ConsMDP(layout="neato")
    m.new_states(11)
    for r in [2,4,9]:
        m.set_reload(r)
    T = {7, 8, 10}

    m.add_action(0,{1:.5,2:.5}, "a", 1)
    m.add_action(0,{3:.5,4:.5}, "t", 3)
    m.add_action(1,{2:1},"",1)
    m.add_action(2,{1:1},"",1)

    m.add_action(3,{2:.5, 7:.5},"p",1)
    m.add_action(3,{5:1},"r",2)
    m.add_action(3,{6:1},"a",3)

    m.add_action(4,{5:1},"",1)
    m.add_action(5,{4:1},"r",1)
    m.add_action(5,{3:1},"t",1)

    m.add_action(6,{7:.5, 10:.5}, "a", 3)
    m.add_action(6,{3:.5, 8:.5}, "B", 6)

    m.add_action(7,{9:1}, "", 1)
    m.add_action(9,{9:1}, "", 1)
    m.add_action(10,{9:1}, "", 1)

    m.add_action(8,{5:1}, "r", 3)

    return m, T
