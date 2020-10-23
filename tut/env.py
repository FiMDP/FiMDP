from fimdpenv import UUVEnv

# Create environment configurations
def create_env(env_name, agent_capacity=200, heading_sd=0.524, reload_input=None):
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

    if env_name == '2R-1T-simple':
        grid_size = (20,20)
        agent_capacity = agent_capacity 
        init_state = 5*grid_size[0]+2
        reload_list = [9*grid_size[0] - 3]
        target_list = [grid_size[0]*grid_size[1] - 3*grid_size[0] - 8]
        
    elif env_name == '2R-1T-complex':
        grid_size = (20,20)
        agent_capacity = agent_capacity 
        init_state = 5*grid_size[0]+2
        reload_list = [2*grid_size[0]+5, 12*grid_size[0] - 5]
        target_list = [grid_size[0]*grid_size[1] - 3*grid_size[0] - 8]

    elif env_name == '4R-5T-complex':
        grid_size = (30,80)
        agent_capacity = agent_capacity 
        init_state = 15*grid_size[1]+ 10
        reload_list = [5*grid_size[1]+20, 5*grid_size[1]+60, 23*grid_size[1]+10, 23*grid_size[1]+70]
        target_list = [5*grid_size[1]+10, 5*grid_size[1]+40, 5*grid_size[1]+70, 27*grid_size[1]+20, 27*grid_size[1]+60]   
        
    elif env_name == '4R-1T-complex':
        grid_size = (30,80)
        agent_capacity = agent_capacity 
        init_state = 5*grid_size[1]+ 10
        reload_list = [5*grid_size[1]+30,5*grid_size[1]+50,17*grid_size[1]+45,20*grid_size[1]+65]
        target_list = [27*grid_size[1]+60]   
    
    else:
        raise Exception("No configuration with that name. Please check the name again")

    if reload_input is None:
        env = UUVEnv.SingleAgentEnv(grid_size, agent_capacity, 
                  reload_list, target_list,
                  init_state=init_state,
                  heading_sd=heading_sd
                  )
    else:
        env = UUVEnv.SingelAgentEnv(grid_size, agent_capacity, reload_input, target_list, init_state=init_state, heading_sd=heading_sd)
    return env