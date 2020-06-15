# -*- coding: utf-8 -*-
"""
Description: minimal working example for creating UUV environment consMDP object and targets
"""
import ast
import numpy as np
import matplotlib.pyplot as plt
from UUVEnv import Env
from energy_solver import *

# input variables
grid_size = (20,20) # size of the grid (required)
agent_velocity = 5 # horizontal velocity of the glider (required)
heading_sd = 0.524 # standard deviation in agent true heading (required)
agent_capacity = 150 # maximum energy capacity of the agent (required)
weakaction_cost= 1 # cost of weak action of the agent (required)
strongaction_cost = 2 # cost of strong action of the agent (required)
init_state = grid_size[0]*5+2 # Initial state of the agent
reload_list = [grid_size[0]*5+2, grid_size[0]*grid_size[1] - 4*grid_size[0] - 10] # list of reload states in the MDP
target_list = [grid_size[0]*grid_size[1] - 3*grid_size[0] - 6, grid_size[0]*grid_size[1] - 3*grid_size[0] - 8] # list of target states in the MDP

env = Env(grid_size, agent_velocity, heading_sd, agent_capacity, weakaction_cost, strongaction_cost, reload_list, target_list, init_state=init_state, render=False)
m, targets = env.create_consmdp()


s = EnergySolver(m, cap=agent_capacity, targets=targets)
strategy = s.get_strategy(AS_REACH, recompute=True)


# policy based on the strategy
def policy(state,energy):
    
    data_dict = strategy[state]
    dict_keys = list(data_dict.keys())
    
    if not bool(dict_keys):
        raise Exception('Strategy does not prescribe a safe action at this state')
    
    feasible = []
    for value in dict_keys:
        if value <= energy:
            feasible.append(value)
    
    action_string = data_dict[max(feasible)]
    action_list = ast.literal_eval(action_string)
    agent_action = action_list[1]
    
    
    return agent_action

# run simulation
while True:

    # info = (next_state, action taken, reward, done)
    energy = env.agent_energy
    state = env.position
    info = env.step(policy(state,energy)) # take action
    print(info)

    if info[0] in target_list:
        break

    if info[3] == 1:
        break


# for state in range(env.num_cells):
#     for action in range(env.num_actions):
   
#         temp = sum(env.agent_P[state,action,:])
        
#         if temp != 1:
#             print(state)
#             print(action)
#             raise Exception('Test failed')