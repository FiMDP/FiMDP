from fimdp.UUVEnv import Env
import ast

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap

myColors = [
    (0.66, 0.66, 0.66, 1.0), # backgroung light gray
    (0.0, 0.3, 0.7, 1.0), # reload blue
    (0.3, 0.3, 0.3, 1.0), # history dark gray
    (0.0, 0.8, 0.0, 1.0),  # targets green
    (0.7, 0.0, 0.0, 1.0), # current position red
]
cmap = ListedColormap(myColors, 5)

# Essential
grid_size = (20,20) # size of the grid
agent_capacity = 200 # maximum energy capacity of the agent
init_state = 2*grid_size[0]+2 # Initial state of the agent
reload_list = [5*grid_size[0]+4, 8*grid_size[0] - 4] # list of reload states in the MDP
target_list = [grid_size[0]*grid_size[1] - 4*grid_size[0] - 9] # list of target states in the MDP

# Non essential
agent_velocity = 5 # horizontal velocity of the glider
weakaction_cost= 1 # cost of weak action of the agent
strongaction_cost = 2 # cost of strong action of the agent
heading_sd = 0.524 # Standard deviation in `true` agent's heading

def create_env(grid_size=grid_size,
               agent_velocity=agent_velocity,
               heading_sd=heading_sd,
               agent_capacity=agent_capacity,
               weakaction_cost=weakaction_cost,
               strongaction_cost=strongaction_cost,
               reload_list=reload_list,
               target_list=target_list,
               init_state=init_state,
               render=False):
    # Generate UUVEnv environment object
    env = Env(grid_size, agent_velocity,
              heading_sd, agent_capacity,
              weakaction_cost, strongaction_cost,
              reload_list, target_list,
              init_state, render=render)
    
    return env

target_reached = 0
    
def get_anim_data(env):
    """Create matrix of colors for rendering the grid-world"""
    data = 0*np.ones([env.grid_size[0],env.grid_size[1]])
    # History
    for cell in env.states_history:
        data[cell//env.grid_size[0], cell%env.grid_size[1]] = 2
    # Targets
    for cell in env.target_list:
        data[cell//env.grid_size[0], cell%env.grid_size[1]] = 3
    # Reloads
    for cell in env.reload_list:
        data[cell//env.grid_size[0], cell%env.grid_size[1]] = 1
    # Current position
    data[env.position // env.grid_size[0], env.position % env.grid_size[1]] = 4
        
    return data

# Function to render the grid world
def next_step_anim(frame, env, strategy, reset=True):
    """Make a next step of `env` according to the strategy and
    update animation.

    Parameters:
    ===========
    frame : int the index of frame to be created. If 0 (and reset = True),
            the environment is reset to initial position.
    env : UUVEnv object to animate
    strategy : counter strategy list[dict{energy -> action}]
    reset : bool if True, environment is reset for the animation for 0th frame
    """
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
    ax.set_title(f"Agent motion: t = {frame}\n" +
                 f"Agent energy: {env.agent_energy}\n" +
                 f"Target reached: {target_reached}")
    return ax,
    

# Function to take action based on the strategy
def policy(strategy, state, energy):
    """Pick the next action of agent based on energy-aware `strategy`,
    its current state and energy.
    """
    action_dict = strategy[state]
    
    if not action_dict:
        raise Exception('Strategy does not prescribe a safe action at this state. Increase the capacity of the agent.')
    pick = max([level for level in action_dict.keys() if level <= energy])
    
    action_string = action_dict[pick]
    # The action labels are of the form "[state, action_id]"
    # We extract the action_id converting it into an actual list
    agent_action = ast.literal_eval(action_string)[1]
    
    return agent_action

def animate_strategy(strategy, environment, steps=100, reset=True):
    """Create animation of the agent moving in `env` using `strategy
    for `steps` steps.
    """
    return animation.FuncAnimation(plt.gcf(), next_step_anim,
                                   fargs=(environment, strategy, reset),
                                   frames=steps,
                                   repeat=False, blit=True)