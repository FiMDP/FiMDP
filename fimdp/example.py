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
agent_capacity = 150 # maximum energy capacity of the agent (required)
init_state = 5*grid_size[0]+2 # Initial state of the agent
reload_list = [10*grid_size[0]+4, 12*grid_size[0] - 5] # list of reload states in the MDP
target_list = [grid_size[0]*grid_size[1] - 3*grid_size[0] - 8] # list of target states in the MDP

# additional inputs
agent_velocity = 5 # horizontal velocity of the glider (required)
heading_sd = 0.524 # standard deviation in agent true heading (required)
weakaction_cost= 1 # cost of weak action of the agent (required)
strongaction_cost = 2 # cost of strong action of the agent (required)


env = Env(grid_size, agent_velocity, heading_sd, agent_capacity, weakaction_cost, strongaction_cost, reload_list, target_list, init_state=init_state, render=True)
m, targets = env.create_consmdp()


s = EnergySolver(m, cap=agent_capacity, targets=targets)
strategy = s.get_strategy(AS_REACH, recompute=True)


# Function to take action based on the strategy
def policy(strategy,state,energy):
    
    data_dict = strategy[state]
    dict_keys = list(data_dict.keys())
    
    if len(dict_keys) == 0:
        raise Exception('Strategy does not prescribe a safe action at this state. Increase the capacity of the agent.')
    feasible = []
    for value in dict_keys:
        if value <= energy:
            feasible.append(value)
    
    action_string = data_dict[max(feasible)]
    agent_action = ast.literal_eval(action_string)[1]
    
    return agent_action
    
    return agent_action

# run simulation
counter = 0
while True:

    # info = (next_state, action taken, reward, done)
    energy = env.agent_energy
    state = env.position
    info = env.step(policy(strategy,state,energy)) # take action
    print(info)
    print("No.of time steps: t = {}".format(counter))
    counter += 1

    # target reached
    if info[0] in target_list:
        print("Target reached. Ending simulation")
        break
    elif info[3] == 1:
        print("Energy exhausted. Ending simulation")
        break
    elif counter >= 500:
        print("Too many steps in simulation for visualization. Ending simulation.")
        break
        
