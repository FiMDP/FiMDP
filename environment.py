from fimdp.UUVEnv import Env
import ast

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap

myColors = [
    '#A9A9A9',            # backgroung light gray
    (0.7, 0.0, 0.0, 1.0), # current position red
    (0.0, 0.3, 0.7, 1.0), # reload blue
    '#5C5959',            # history dark gray
    (0.0, 0.8, 0.0, 1.0)  # targets green
]
cmap = ListedColormap(myColors, 5)

# Essential
grid_size = (20,20) # size of the grid
#agent_capacity = 200 # maximum energy capacity of the agent
init_state = 2*grid_size[0]+2 # Initial state of the agent
reload_list = [5*grid_size[0]+4, 8*grid_size[0] - 4] # list of reload states in the MDP
target_list = [grid_size[0]*grid_size[1] - 4*grid_size[0] - 9] # list of target states in the MDP

def env(agent_capacity=200, heading_sd=0.524):
    # Non essential 
    agent_velocity = 5 # horizontal velocity of the glider
    weakaction_cost= 1 # cost of weak action of the agent
    strongaction_cost = 2 # cost of strong action of the agent

    # Generate MDP and export to consMDP
    env = Env(grid_size, agent_velocity, heading_sd, agent_capacity, weakaction_cost, strongaction_cost, reload_list, target_list, init_state=init_state, render=False)
    
    return env

data = None
target_reached = 0
    
def get_anim_data(env):
    data = 0*np.ones([env.grid_size[0],env.grid_size[1]])
    for cell in env.states_history:
        data[cell//env.grid_size[0], cell%env.grid_size[1]] = 3
    data[env.position//env.grid_size[0], env.position%env.grid_size[1]] = 1
    for cell in env.target_list:
        data[cell//env.grid_size[0], cell%env.grid_size[1]] = 4
    for cell in env.reload_list:
        data[cell//env.grid_size[0], cell%env.grid_size[1]] = 2
        
    return data

# Function to render the grid world
def next_step_anim(frame, env, strategy, reset=True):
    global target_reached
    if frame == 0:
        if reset:
            env.reset(init_state)
            target_reached = 0
    else:
        energy = env.agent_energy
        state = env.position
        info = env.step(policy(strategy,state,energy)) # take action
    
    if env.position in target_list:
        target_reached += 1
    
    data = get_anim_data(env)       
    #plt.clf()
    ax = sns.heatmap(data, cmap=cmap, cbar =False, linewidths=.5, linecolor='lightgray')
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    ax.set_title(f"Agent motion: t = {frame}\nAgent energy: {env.agent_energy}\nTarget reached: {target_reached}")
    return ax,
    #plt.pause(0.01)
    

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

e = env()
def animate_strategy(strategy, env=e, steps=100, reset=True):
    #update = lambda frame: next_step_anim(frame, env, strategy, reset=reset)
    return animation.FuncAnimation(plt.gcf(), next_step_anim, fargs=(env, strategy, reset), frames=steps,
                                       repeat=False, blit=True)