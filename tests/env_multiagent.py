from UUVEnv import SynchronousMultiAgentEnv
import fimdp
from fimdp.energy_solver import GoalLeaningES
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def setup():
    
    """
    Setup base configuration for animation
    """
    from matplotlib import animation, rc
    rc('animation', html='jshtml')


# Create environment configurations
def create_env(agent_capacity):
    '''
    Create different environments with different grid sizes, target states, and reload
    states
    
    Parameters
    ----------
    env_name : TYPE
        DESCRIPTION.
    agent_capacity : TYPE, optional
        DESCRIPTION. The default is 200.
    heading_sd : TYPE, optional
        DESCRIPTION. The default is 0.524.
    reload_input : TYPE, optional
        DESCRIPTION. The default is None.
    Raises
    ------
    Exception
        DESCRIPTION.
    Returns
    -------
    env : TYPE
        DESCRIPTION.
    '''

    grid_size = (20,20)
    init_state = [7*grid_size[0]+2, 7*grid_size[0]+2, 7*grid_size[0]+2]
    reload_list = [2*grid_size[0]+5, 12*grid_size[0] - 5]
    targets_list = [[345],[24, 44, 57, 156],[71, 87, 102, 232, 191]]
    env = SynchronousMultiAgentEnv(3, grid_size, agent_capacity, reload_list, targets_list, init_state=init_state)
    return env


def visualize_allocation(e):
    """
    Function to visualize how different target sets are allocated to different agents
    """
    
    COLORS_TRAJEC = {0:np.array([0.45,0.45,0.45]), 1:np.array([0.71,0.71,0.71]), 2:np.array([0.32,0.32,0.32])}
    targets_sets = e.targets_list

    data = np.zeros([e.grid_size[0],e.grid_size[1],3],dtype=np.float32)
    data[:] = np.array([0.85,1.0,1.0])
    for cell in e.reload_list:
        data[cell//e.grid_size[1], cell%e.grid_size[1]] = np.array([1.0,0.37,0.008]) # reloads
    for i in range(e.num_agents):
        for cell in targets_sets[i]:
            data[cell//e.grid_size[1], cell%e.grid_size[1]] = COLORS_TRAJEC[i]
    data[e.init_state[0]//e.grid_size[1], e.init_state[0]%e.grid_size[1]] = np.array([0.0,0.0,1.0]) # home/base
    
    img_data = data
    fig, ax = plt.subplots()
    ax.axis('off')
    plt.title("Energy: {}, Time Steps: {}".format(e.agent_energy, e.time_steps))
    plt.imshow(img_data) 
    plt.show()
    

def animate_multipletargets(env, capacities_list, num_steps=100, interval=100):
    
    """
    Function that runs an instance of simulation and animates the resultant trajectories
    for multi-agent scenario where each agent has its own allocated target set. 
    """
    
    # Update consMDP energy and targets
    env.agent_capacity = capacities_list
    targets_list = [[345],[24, 44, 57, 156],[71, 87, 102, 232, 191]]
    env.target_list = targets_list
    env.create_consmdp()
    m, temp = env.get_consmdp()
    
    # List of all targets
    targets_all = []
    for list in targets_list:
        targets_all = targets_all + list
    targets_all += env.init_state
        
    # dictionary of strategies to reach each of the target
    strategies_dict = {}
    for target in targets_all:
        solver = GoalLeaningES(m, env.agent_capacity[0], [target], threshold=0.1)
        strategy = solver.get_strategy(fimdp.energy_solver.BUCHI)
        strategies_dict[target] = strategy
    
    #simulation and animation
    env.reset(env.init_state)
    fig = plt.figure()
    ax = fig.gca()
    ax.axis('off')
    im = plt.imshow(env._states_to_colors(), animated=True)
    for agent_id in range(env.num_agents):
        env.targets_history[agent_id] =  [env.init_state[agent_id]] + targets_list[agent_id]
    plt.close()
    
    def updatefig(frame_count):
        
        mapping = [0,0,0]
        # mapping from inital state and a target state to next target state
        mapping[0] = {env.init_state[0]:345, 345:env.init_state[0]}
        mapping[1] = {env.init_state[1]:24, 24:44, 44:57, 57:156, 156:env.init_state[1]}
        mapping[2] = {env.init_state[2]:102, 102:71, 71:87, 87:191, 191:232, 232:env.init_state[2]}
        
        if frame_count == 0: 
            env.reset()
            for agent_id in range(env.num_agents):
                env.update_strategy(agent_id, strategies_dict[mapping[agent_id][env.init_state[agent_id]]])  
            
            im.set_array(env._states_to_colors())
            ax.set_title("Energy: {}, Time Steps: {}".format(env.agent_energy, env.time_steps))
            return im
        
        else:
            for agent_id in range(env.num_agents):    
                if env.position[agent_id] in env.targets_history[agent_id]:
                    env.update_strategy(agent_id, strategies_dict[mapping[agent_id][env.position[agent_id]]])  
                    env.targets_history[agent_id].remove(env.position[agent_id])
            
        # pick action and plot
        env.step(env.pick_action())
        im.set_array(env._states_to_colors())
        ax.set_title("Energy: {}, Time Steps: {}".format(env.agent_energy, env.time_steps))
        return im
    
    anim = animation.FuncAnimation(fig, updatefig, frames=num_steps, interval=interval)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=7, metadata=dict(artist='Me'), bitrate=1800)
    anim.save('anim.mp4', writer=writer)
    return anim