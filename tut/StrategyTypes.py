# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Strategy types
# The package offeres several solvers that can generate strategies for the considered objectives. In this notebook focus on the Büchi objective and we discuss solvers that all:
#  * solve almost-sure Büchi objective and
#  * compute the minimal initial load needed in each state.
# In other words, all the solvers have the same guarantees. Where they differ are the strategies they produce. Our overall goal is to provide strategies that not only provide these guarantees, but are also **usable in practical control case studies**.
#
# We use a simple gridworld underwater environment generated by [FiMDPEnv] to demonstrate the behavior we can obtain using different solvers of the [FiMDP] package. We have some pre-defined environments in the file [env.py](env.py). The goal of the agent is to reach the green target with sufficient energy so that it can reach it again and again.
#
# In each cell of the gridworld, the agent can choose one of eight possible actions. For each of the 4 directions (`NORTH`, `SOUTH`, `WEST`, `EAST`) he can choose whether to play a *weak* or _strong_ action. A strong action costs more energy, while the weak action has uncertain outcome. The resulting direction of movement can be affected by pre-defined currents. In most cases, picking `EAST` can, with small probability end up with the agent going `SOUTH` or `NORTH`.
#
# [FiMDP]: https://github.com/xblahoud/FiMDP
# [FiMDPEnv]: https://github.com/pthangeda/FiMDPEnv

# %matplotlib widget
from fimdpenv import UUVEnv
from env import create_env

e = create_env('2R-1T-simple', heading_sd=0.32, agent_capacity=40)
e

# The colors of the gridworld cells have teh following semantics:
#  * <font color='blue'>Blue Cell</font>: Current location of the agent
#  * <font color='gray'>Gray Cells</font>: Trajectory of the agent
#  * <font color='green'>Green Cells</font>: Target States
#  * <font color='orange'>Orange Cells</font>: Reload states

# This package offers 3 solvers that generate strategies:
#  * Basic solver (class `EnergySolver`)
#  * Goal-leaning solver (class `EnergySolver_GoalLeaning`)
#  * Threshold solver (class `EnergySolver_ThresholdGoalLeaning`)

# +
import fimdp

def showcase_solver(SolverClass, gw=e, steps=100, capacity=40):
    gw.agent_capacity=capacity
    m, t = gw.create_consmdp()
    solver = SolverClass(m, capacity, t)
    strategy = solver.get_strategy(fimdp.energy_solver.BUCHI)
    gw.animate_strategy(strategy, num_steps=steps)
    
def strategy_at(SolverClass, state, gw=e, steps=100, capacity=40):
    gw.agent_capacity=capacity
    m, t = gw.create_consmdp()
    solver = SolverClass(m, capacity, t)
    strategy = solver.get_strategy(fimdp.energy_solver.BUCHI)
    return strategy[state]

reload = e.create_consmdp()[0].reloads.index(True)
# -

# ## Basic solver
# Let's first look what happens when we apply the algorithm presented at [CAV'2020] without any modification on our problem.
#
# The basic algorithm does not take probabilities of outcomes into account at all. This is a standard approach in quantitative algorithms for MDPs.
#
# [CAV'2020]: https://i-cav.org/2020/

from fimdp.energy_solver import EnergySolver
showcase_solver(EnergySolver, capacity=40)

# While the generated strategy guarantees that the agent eventually reaches the target with probability 1, it make take enourmous number of steps before it really happens. As the basic solver does ignore probabilities of action-outcomes complete, all actions with `WEST` as a possible outcome to `WEST` are equally good. The order of actions processed by the algorithm starts with `NORTH`, and thus `NORTH` is often chosen instead of `EAST`. But the agent only moves to `EAST` on rare events.

strategy_at(EnergySolver, reload, capacity=40)

# Above, we can see that for all values of energy, the strategy chooses action labeled `[45, 0]` in the reload state. The `45` is the id of the reload state, and `0` stands for `NORTH`.

# ## Goal-leaning solver
# The goal-leaning solver aims to solve the issue of the *Basic solver*. It does not ignore the probabilities on edges. 
#
# When choosing from equally good actions, this solver chooses the most-likely successful action.
#
# #### More technical explenation
# The measure of *goodness* in the sentence above means *low value of `action_value_T`, which is the amount of energy needed to satisfy the objective*. The `action_value_T` is $\mathit{SPR-Val}$ in the CAV paper. In contrast with the Basic solver, `action_value_T` returns not only the action value, but also the probability that the outcome of this action will the one that produced this value. Then from actions with minimal value we choose the one with the highest probability of reaching the desired outcome.

from fimdp.energy_solver import EnergySolver_GoalLeaning
showcase_solver(EnergySolver_GoalLeaning, capacity=40)

strategy_at(EnergySolver_GoalLeaning, reload, capacity=40)

# This looks much better. We can see that now the picked action is `[45, 1]`, where `1` translates to `EAST`. 
#
# However, in certain situations, strategies generated by the Goal-leaning solver do not work well. Consider the following scenario with capacity that is slightly lower.

from fimdp.energy_solver import EnergySolver_GoalLeaning
showcase_solver(EnergySolver_GoalLeaning, capacity=35)

# The reason why the agent does not pick `EAST` when being in the half on his route is that `EAST` is not among the actions with the lowest value. The higher value is caused by $\mathit{Safe}$-value for `SOUTH`, which is a possible outcome of `EAST`. Intuitivelly, $\mathit{Safe}$-value of a state is the minimum level of energy needed to survive from this state and in our scenario it loosely translates to distance from reload states. These values of all possible outcomes also influence the `action_value_T`. In the case above, all possible outcomes of the action `NORTH` have lower $\mathit{Safe}$-value than the state `SOUTH` and thus all actions with `SOUTH` as a possible outcome are disregarded by this solver. As a result, `NORTH` is the only action considered and even though the desired outcome (`EAST` in this case) has a low probability, `NORTH` is the winner.

problematic = 187
strategy_at(EnergySolver_GoalLeaning, problematic)

# This is the strategy at the problematic spot. We can see, that with energy between 18 and 27, the agent picks `0`, which is `NORTH`. The agent with capacity 35 can only reach this spot from the top reload state with capacity 26, which is in this interval. With 40, the energy 31 is feasible in this spot and thus we did not see such behaviour.

# ## Threshold solver

# The last solver overcomes the issue from above by introducing a threshold on desired outcomes of actions it considers. Loosely speaking, when computing `action_value_T`, we disregard possible outcomes that are less likely then the given threshold. As a result, it only considers `NORTH` as the desired outcome of action `NORTH` when computing `action_value_T`.
#
# Ignoring the rare cases can lead to increase in the minimal energy we need to satisfy the objective. For example, in the problematic case above, `NORTH` will have higher `action_value_T` with the threshold, which means that its previous value is no longer achieved. Therefore, after reaching the fixpoint for the first time (using the threshold-approach), we run another fixpoint that can improve the current values not using the threshold.

from fimdp.energy_solver import EnergySolver_ThresholdGoalLeaning
solver_class = lambda mdp, cap, t: EnergySolver_ThresholdGoalLeaning(mdp, cap, t, threshold=0.1)
showcase_solver(solver_class, capacity=35)

problematic = 187
strategy_at(solver_class, problematic, capacity=35)

# This strategy uses the strong actions (`4`—`7`) for energy between 16 and 27. It goes `NORTH=4` only with interval 16—18, and prefers to go to `SOUTH=6` with energy in 19—28, and finally uses weak action to `EAST` with more than 27 units of energy.

# ## Equivalent values

# In this section we show that the new solvers are actually improving the Basic solver, while maintaining the same minimal energy levels needed to fulfill the objectives. These values can be obtained by calling the `get_Buchi` on the solvers.

m, t = e.create_consmdp()
basic = EnergySolver(m, cap=35, targets=t)
goal = EnergySolver_GoalLeaning(m, cap=35, targets=t)
threshold = EnergySolver_ThresholdGoalLeaning(m, cap=35, targets=t, threshold=0.1)

assert basic.get_Buchi() == goal.get_Buchi(), ("The basic and goal-leaning strategy "+
                                              "do not reach the same values of "+
                                              "initial load for the same task.")
print("Passed test 1 for values of goal-leaning strategies in file tut/StrategyTypes.ipynb")
assert basic.get_Buchi() == threshold.get_Buchi(), ("The basic and the threshold strategy "+
                                              "do not reach the same values of "+
                                              "initial load for the same task.")
print("Passed test 2 for values of goal-leaning strategies in file tut/StrategyTypes.ipynb")

# ## Interesting cases
#
# ### Sure path with 2 steps better than unlikely 1-step path.

# ![threshold example](threshold_example.svg)
# All actions having consumption 1, not-listed probabilities are also 1, rel are reload states.
#
# Now let's create the CMDP using the FiMDP package.

from fimdp import dot
dot.dotpr = "neato"

# +
two_step = fimdp.consMDP.ConsMDP()

two_step.new_states(4)
two_step.set_reload(1)
two_step.set_reload(3)
two_step.add_action(0, {1: .99, 3: .01}, "direct", 1)
two_step.add_action(1, {0: 1}, "", 1)
two_step.add_action(0, {2: 1}, "long", 1)
two_step.add_action(2, {3: 1}, "long", 1)
two_step.add_action(3, {3: 1}, "rel", 1);

two_step
# -

from fimdp.energy_solver import BUCHI
basic = EnergySolver(two_step, targets=[3])
goal = EnergySolver_GoalLeaning(two_step, targets=[3])
threshold = EnergySolver_ThresholdGoalLeaning(two_step, targets=[3], threshold=0.011)

# Intuitivelly, if we want to reach the target quickly, we need to take the upper path (via state 2) and we surely reach the target (double circled) in 2 steps. The lower path (via state 1) reaches the target with very low probability; trying infinitely often will leads us to the target almost surely, though.
#
# The basic solver chooses the action `direct` that goes to the lower state. The same holds for the goal-leaning solver. With the treshold being $> 0.01$ the threshold solver goes via the lower path only with energy=1 (using the below-treshold value from the second fix-point), otherwise it prefers the upper path.

basic.get_strategy(BUCHI)

goal.get_strategy(BUCHI)

threshold.get_strategy(BUCHI)

result = threshold.get_strategy(BUCHI)[0]
expected = {2: 'long', 1: 'direct'}
assert result == expected, ("The threshold strategy should return\n" +
                           f"{expected} in state 0.\n" +
                           f"{result} returned in 0.")
print("Passed test 3 for the threshold strategy in file tut/StrategyTypes.ipynb")

# ### Simple goal-leaning example

# +
goal_leaning = fimdp.consMDP.ConsMDP()

goal_leaning.new_states(4)
goal_leaning.set_reload(1)
goal_leaning.set_reload(3)
goal_leaning.add_action(0, {1: .99, 3: .01}, "direct", 1)
goal_leaning.add_action(1, {0: 1}, "", 1)
goal_leaning.add_action(0, {2: 1}, "long", 1)
goal_leaning.add_action(2, {3: 1}, "long", 1)
goal_leaning.add_action(3, {3: 1}, "rel", 1);

goal_leaning


# +
def goal_leaning():
    dot.dotpr = "dot"
    m = fimdp.consMDP.ConsMDP()
    m.new_states(3)
    for r in [0, 2]:
        m.set_reload(r)
    m.add_action(0, {1:.5, 0:.5}, "top", 1)
    m.add_action(0,{1:.7, 0:.3},"bottom",1)
    m.add_action(1,{2:1}, "r", 1)
    m.add_action(2,{2:1}, "r", 2)

    targets=set([2])
    return m, targets

gl, T = goal_leaning()
gl.get_Buchi(T)
gl
# -

basic = EnergySolver(gl, targets=T)
goal = EnergySolver_GoalLeaning(gl, targets=T)

# In state 0, the standard solver (`basic`) chooses the `top` action because it is processed first and `bottom` does not yield any better value. You can change the order of the actions in the function that creates the CMDP and see that the result for `basic` changes.
#
# The goal-leaning solver, however, chooses `bottom` as it yields a higher probability of reaching the state 1, which is the successor that has good promise to reach a target.

print(basic.get_strategy(BUCHI), goal.get_strategy(BUCHI), sep="\n")

result = goal.get_strategy(BUCHI)[0][0]
expected = 'bottom'
assert result == expected, (
    f"The goal-leaning strategy should prefer the action `{expected}` " +
    f"in state 0. It chooses `{result}` instead."
)
print("Passed test 4 for goal-leaning solver in file tut/StrategyTypes.ipynb")


# ### Goal-leaning is just a heuristic
# We slightly modify the previous example by adding a new state (3), which is a copy of state 1. The `top` action, now named `sure`, does not loop back to 0, instead it goes either to 1 or 2. This results in a situation where picking the `sure` action surely leads to the targets. But when deciding which action to choose, the solvers always consider only 1 successor. The best the action `sure` can achieve in this view is `0.5` reaching a promising successor. Therefore, the goal-leaning solver still prefers the bottom action, now called `cycle`. The `basic` solver still chooses the action that comes first as they both can achieve the same value.

# +
def goal_leaning_2():
    dot.dotpr = "dot"
    m = fimdp.consMDP.ConsMDP()
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

gl2, T = goal_leaning_2()
gl2.get_Buchi(T)
gl2
# -

basic2 = EnergySolver(gl2, targets=T)
goal2 = EnergySolver_GoalLeaning(gl2, targets=T)

print(basic2.get_strategy(BUCHI), goal2.get_strategy(BUCHI), sep="\n")