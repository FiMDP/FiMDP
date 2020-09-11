"""
Gridworld modeling motion of a constant horizontal velocity UUV in waters
with ocean currents.
"""

# import required packages
import ast
import numpy as np
from fimdp import consMDP
from decimal import Decimal
from matplotlib import pyplot as plt
from scipy.stats import norm
import matplotlib.animation as animation


class SingleAgentEnv:

    def __init__(self, grid_size, agent_capacity, reload_list, targets_list, init_state=None, agent_velocity=5, heading_sd=0.524, weakaction_cost=1, strongaction_cost=2):
        """Class that models a Markov Decision Process where the agent and the environment model the dynamics of a UUV and 
        the ocean currents it is operating in.  

        :param grid_size: tuple (m,n) of length two with positive integers that denotes the dimensions of the 2D grid to be generated. 
        :type grid_size: int
        :param agent_capacity: Non negative number denoting the energy capacity of the agent
        :type agent_capacity: float
        :param waction_cost: Positive number that denotes the energy consumed by the agent for any weak action.
        :type waction_cost: float
        :param saction_cost: Positive number that denotes the energy consumed by the agent for any strong action.
        :type saction_cost: float
        :param init_state: An integer denoting the initial state of the agent, defaults to None
        :type init_state: int, optional
        """

        # user inputs and other required constants
        self.grid_size = grid_size
        self.agent_capacity = agent_capacity
        self.waction_cost = weakaction_cost
        self.saction_cost = strongaction_cost
        self.reload_list = reload_list
        self.targets_list = targets_list
        self.init_state = init_state
        self.position = None
        self.strategy = None
        self.states_history = []
        self.actions_history = []
        self.targets_history = []
        self.time_steps = 0
        self.consmdp = None
        

        # initialize required variables
        self.num_cells = grid_size[0]*grid_size[1]
        self.num_actions = 8
        self.is_reload = np.zeros(self.num_cells)
        self.agent_energy = self.agent_capacity
        self.agent_P = np.zeros(
            [self.num_cells, self.num_actions, self.num_cells])

        # initialize and generate current flow field -- DEMO CONFIG ONLY
        self.AGENT_V = agent_velocity
        self.HEADING_SD = heading_sd
        self.FLOW_VX = 0.1*self.AGENT_V * \
            np.ones([self.num_cells, self.num_cells])
        self.FLOW_VY = 0.2*self.AGENT_V * \
            np.ones([self.num_cells, self.num_cells])
        self.FLOW_MAG = np.hypot(self.FLOW_VX, self.FLOW_VY)
        self.FLOW_THETA = np.arctan2(self.FLOW_VY, self.FLOW_VX)
        self.THETA_LIST = [np.pi/2, -np.pi/2, 0, np.pi]

        # generate state transition probabilities
        for i in range(self.num_cells):
            for j in range(self.num_actions):

                # north, strong north - action 0 and action 4
                if j in [0, 4]:
                    if i - self.grid_size[1] < 0:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i-self.grid_size[1]
                                     ] = Decimal(str(1))

                # south, strong south - action 1 and action 5
                elif j in [1, 5]:
                    if i + self.grid_size[1] >= self.num_cells:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i+self.grid_size[1]
                                     ] = Decimal(str(1))

                # east, strong east - action 2 and action 6
                elif j in [2, 6]:
                    if i % self.grid_size[1] == self.grid_size[1]-1:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i+1] = Decimal(str(1))

                # west, strong west - action 3 and action 7
                elif j in [3, 7]:
                    if i % self.grid_size[1] == 0:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i-1] = Decimal(str(1))

                if not ((i - self.grid_size[1] < 0) or
                        (i + self.grid_size[1] >= self.num_cells) or
                        (i % self.grid_size[1] == self.grid_size[1]-1) or
                        (i % self.grid_size[1] == 0)):

                    # generate stochastic dynamics for weak actions 
                    if j in [0, 1, 2, 3]:
                        self.agent_P[i, j, :] = self._generate(i, j)
                        
        # initialize agent and environment
        self.reset(self.init_state)
        self._add_reloads()


    def _generate(self, s, a):
        '''
        Given state and action, generate the transition probability array and
        the reload states for weak actions.
        '''
        # combined actual heading
        actual_x = self.AGENT_V*np.cos(self.THETA_LIST[a]) + self.FLOW_MAG[s,a]*np.cos(self.FLOW_THETA[s, a])
        actual_y = self.AGENT_V*np.sin(self.THETA_LIST[a]) + self.FLOW_MAG[s,a]*np.sin(self.FLOW_THETA[s, a])
        actual_theta = np.arctan2(actual_y, actual_x)
        rv = norm(actual_theta, self.HEADING_SD)

        # calculate TP
        tp = np.zeros(self.num_cells)
        tp[s-self.grid_size[1]] = p_n = Decimal(str(round(rv.cdf(3*np.pi/4) - rv.cdf(np.pi/4), 3)))
        tp[s+self.grid_size[1]] = p_s = Decimal(str(round(rv.cdf(-np.pi/4) - rv.cdf(-3*np.pi/4), 3)))
        tp[s+1] = p_e = Decimal(str(round(rv.cdf(np.pi/4) - rv.cdf(-np.pi/4), 3)))
        diff = Decimal(str(round(1 - (p_n + p_s + p_e),3)))
        if p_n + p_s + p_e > Decimal(1):
            tp[s-1] = Decimal(str(0))
            tp[s+1] = Decimal(str(round(Decimal(tp[s+1]) - diff,3))) 
        else:
            tp[s-1] = diff
        return tp
    
    
    def update_strategy(self, strategy):
        '''
        Update the strategy attribute to the given strategy
        '''
        self.strategy = strategy
    
            
    def pick_action(self, strategy=None, state=None, energy=None):
        '''
        Given strategy, current state, and current energy level pick the next
        action of the agent
        '''
        if state==None:
            state = self.position
        if energy==None:
            energy = self.agent_energy
        if strategy==None:
            strategy = self.strategy
            if strategy == None:
                raise Exception('Add the strategy by using env.update_strategy method')
        data_dict = self.strategy[state]
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
        

    def step(self, action, do_render=0):
        '''
        Given action, function step updates the state of the agent and returns
        the resultant state, cap, and other info
        '''

        # initialize variables
        done = 0
        if self.agent_energy < self.saction_cost:
            raise Exception('Warning: energy too low to take strong action.')
        
        # verify action input and decide action
        if isinstance(action, int) and action in list(range(self.num_agents)):
            self.position = np.random.choice(self.num_cells,
                                             p=self.agent_P[self.position, action, :])
        else:
            raise Exception('Input action is not a valid action')

        # update energy
        if action in [0,1,2,3]:
            self.agent_energy -= self.waction_cost
        else:
            self.agent_energy -= self.saction_cost
        if self.is_reload[self.position]:
            self.agent_energy = self.agent_capacity
        
        # energy exhaustion check
        if self.agent_energy <= 1 and self.agent_energy >= 0:
            done = 1
       
        # update other terms
        self.states_history.append(self.position)
        self.actions_history.append(action)
        self.time_steps += 1
        
        # render and return
        if do_render == 1:
            self.render_grid()
        info = (self.position, action, self.agent_energy, done)
        return info
    

    def reset(self, init_state=None, reset_energy=None):

        # random initial position
        if init_state == None:
            self.position = np.random.randint(self.num_cells)
        else:
            if 0 <= init_state < self.num_cells and isinstance(init_state, int):
                self.position = init_state
            else:
                raise Exception(
                    'states should be integers between 0 and num_cells. Check init_state again')
                
        if reset_energy == None:
            self.agent_energy = self.agent_capacity
        else:
            self.agent_energy = reset_energy
        self.states_history = [self.position]
        self.actions_history = []
        self.targets_history = []
        self.time_steps = 0
    

    def _add_reloads(self):    
        """
        Internal method to assign reload states.
        """        
        for state in self.reload_list:
            self.is_reload[state] = 1
            
        
    def _get_dist(self, mdp, state, action):
        """
        Internal method that returns a dictionary of states with nonzero probabilities for
        a given state and action
        """
        dist = dict()
        agent_dist = self.agent_P[state, action, :]
        agent_posstates = [] 
        for i in agent_dist.nonzero()[0]:
            agent_posstates.append(i)
        for i in list(agent_posstates):
            prob = agent_dist[i]
            dist[i] = prob
        return dist
    
    
    def create_consmdp(self):
        """
        Method to export the UUV gridworld and target states into a pre-defined
        standard consMDP form. Returns MDP object and the target set.
        """
        mdp = consMDP.ConsMDP()
    
        # Add states
        for i in range(self.num_cells):
            if self.is_reload[i]:
                mdp.new_state(True, str(i))  # (reload, label)
            else:
                mdp.new_state(False, str(i))
                
        # List all possible states and actions
        states_list = []
        for i in range(self.num_cells):
                states_list.append(i)
            
        actions_list = []
        for i in range(self.num_actions):
                actions_list.append(i)        

        # Extract and add actions to the MDP
        actions = dict()
        for state in states_list:
            for action in actions_list:
                action_label = str([state,action])
                dist = self._get_dist(mdp, state, action)
                if action in [0,1,2,3]: # weak action
                    actions[action_label] = {"from":str(state), "cons":self.waction_cost, "dist":dist}
                else: # strong action
                    actions[action_label] = {"from":str(state), "cons":self.saction_cost, "dist":dist}
                
        for label, act in actions.items():
            fr = mdp.state_with_name(act["from"])
            mdp.add_action(fr, act["dist"], label, act["cons"])
        
        self.consmdp = mdp
    
    
    def get_consmdp(self):
        """
        Method that returns the consMDP object and target set that already exists
        or generates it if it does not exist
        """
        
        if self.consmdp == None:
            self.create_consmdp()
            return (self.consmdp, self.targets_list)
        else:
            return (self.consmdp, self.targets_list)

    
    def _states_to_colors(self):
        '''
        Assign colors to the cells based on their current identity.
        '''
        
        # Define colors
        # 0: light blue; 1 : light gray; 2 : dark gray; 3 : green; 4 : orange; 5: dark blue
        COLORS = {0:np.array([0.85,1.0,1.0]), 1:np.array([0.54,0.54,0.54]), \
                  2:np.array([0.42,0.42,0.42]), 3:np.array([0.0,1.0,0.0]), \
                      4:np.array([1.0,0.37,0.008]), 5:np.array([0.0,0.0,1.0])}
        
        data = np.zeros([self.grid_size[0],self.grid_size[1],3],dtype=np.float32)
        data[:] = COLORS[0] # baseline state color
        for cell in self.states_history:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[2] # history
        for cell in self.targets_list:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[3] # targets
        for cell in self.reload_list:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[4] # reloads
        data[self.position//self.grid_size[1], self.position%self.grid_size[1]] = COLORS[5] # current state
        return data


    def render_grid(self):
        
        img_data = self._states_to_colors()
        fig, ax = plt.subplots()
        ax.axis('off')
        plt.title("Agent Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
        plt.imshow(img_data) 
        plt.show()


    def animate_strategy(self, strategy=None, num_steps=100, interval=100):
        '''
        Run the strategy and animate for num_steps no.of time steps
        '''
        
        if strategy != None:
            self.strategy = strategy
        self.reset(self.init_state)
        fig = plt.figure()
        ax = fig.gca()
        ax.axis('off')
        im = plt.imshow(self._states_to_colors(), animated=True)
        plt.close()
        
        def updatefig(frame_count):
            
            if frame_count == 0:
                im.set_array(self._states_to_colors())
                ax.set_title("Agent Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
                return im
            self.step(self.pick_action())
            im.set_array(self._states_to_colors())
            ax.set_title("Agent Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
            return im
        return animation.FuncAnimation(fig, updatefig, frames=num_steps, interval=interval)
        
        
    def _states_to_colors_dev(self):
        '''
        Assign colors to the cells based on their current identity.
        '''
   
        # Define colors
        # 0: light blue; 1 : light gray; 2 : dark gray; 3 : green; 4 : orange; 5: dark blue
        COLORS = {0:np.array([0.85,1.0,1.0]), 1:np.array([0.54,0.54,0.54]), \
                  2:np.array([0.42,0.42,0.42]), 3:np.array([0.0,1.0,0.0]), \
                      4:np.array([1.0,0.37,0.008]), 5:np.array([0.0,0.0,1.0])}
        
        data = np.zeros([self.grid_size[0],self.grid_size[1],3],dtype=np.float32)
        data[:] = COLORS[0] # baseline state color
        
        # separate strong and weak outcomes
        states_strongoutcome = []
        states_weakoutcome = []
        
        for index, action in enumerate(self.actions_history):
            if action in [0,1,2,3]:
                states_weakoutcome.append(self.states_history[index+1])
            elif action in [4,5,6,7]:
                states_strongoutcome.append(self.states_history[index+1])
        
        for cell in states_strongoutcome:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[2] # strong outcomes
        for cell in states_weakoutcome:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[1] # weak outcomes
        for cell in self.targets_list:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[3] # targets
        for cell in self.reload_list:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[4] # reloads
        data[self.position//self.grid_size[1], self.position%self.grid_size[1]] = COLORS[5] # current state
        return data
    
    def animate_strategy_dev(self, strategy=None, num_steps=100, interval=100):
        '''
        Run the strategy and animate for num_steps no.of time steps while highlighting
        outcomes of strong and weak actions separately
        '''
        
        if strategy != None:
            self.strategy = strategy
        self.reset(self.init_state)
        fig = plt.figure()
        ax = fig.gca()
        ax.axis('off')
        im = plt.imshow(self._states_to_colors_dev(), animated=True)
        plt.close()
        
        def updatefig(frame_count):
            if frame_count == 0:
                im.set_array(self._states_to_colors())
                ax.set_title("Agent Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
                return im            
            self.step(self.pick_action())
            im.set_array(self._states_to_colors_dev())
            ax.set_title("Agent Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
            return im
        return animation.FuncAnimation(fig, updatefig, frames=num_steps, interval=interval)


    def _repr_png_(self):
        '''
        Show graphical representation in notebooks.
        '''
        return self.render_grid()
    

class SynchronousMultiAgentEnv:

    def __init__(self, num_agents, grid_size, agent_capacity, reload_list, targets_list, init_state=None, agent_velocity=5, heading_sd=0.524, weakaction_cost=1, strongaction_cost=2):
        """Class that models a Markov Decision Process representing the stochastic dynamics of a multiple UUVS and 
        the ocean currents they are operating in. It is assumed that all agents act synchronously. We also assume that all agents
        can access all the reload states. 

        :param grid_size: tuple (m,n) of length two with positive integers that denotes the dimensions of the 2D grid to be generated. 
        :type grid_size: int
        :param agent_capacity: Non negative number denoting the energy capacity of the agent
        :type agent_capacity: float
        :param waction_cost: Positive number that denotes the energy consumed by the agent for any weak action.
        :type waction_cost: float
        :param saction_cost: Positive number that denotes the energy consumed by the agent for any strong action.
        :type saction_cost: float
        :param init_state: An integer denoting the initial state of the agent, defaults to None
        :type init_state: int, optional
        """

        # user inputs and other required constants
        self.num_agents = num_agents
        self.grid_size = grid_size
        self.agent_capacity = agent_capacity # array of capacities of different agents
        self.waction_cost = weakaction_cost # array of weak action cost of different agents
        self.saction_cost = strongaction_cost # array of strong action cost of different agents
        self.reload_list = reload_list # array of all reload states
        self.targets_list = targets_list # array containing lists of target states of each agent
        self.init_state = init_state # array of initial states of different agents
        self.position = [None for i in range(self.num_agents)]
        self.strategy = [None for i in range(self.num_agents)]
        self.states_history = [[] for i in range(self.num_agents)]
        self.actions_history = [[] for i in range(self.num_agents)]
        self.targets_history = [[] for i in range(self.num_agents)]
        self.time_steps = 0
        self.consmdp = None
        
        # other required variables
        self.targets_all = []
        for list in targets_list:
            self.targets_all += list
        self.num_cells = grid_size[0]*grid_size[1]
        self.num_actions = 8
        self.is_reload = np.zeros(self.num_cells)
        self.agent_energy = self.agent_capacity
        self.agent_P = np.zeros(
            [self.num_cells, self.num_actions, self.num_cells])

        # initialize and generate current flow field -- DEMO CONFIG ONLY
        self.AGENT_V = agent_velocity
        self.HEADING_SD = heading_sd
        self.FLOW_VX = 0.1*self.AGENT_V * \
            np.ones([self.num_cells, self.num_cells])
        self.FLOW_VY = 0.2*self.AGENT_V * \
            np.ones([self.num_cells, self.num_cells])
        self.FLOW_MAG = np.hypot(self.FLOW_VX, self.FLOW_VY)
        self.FLOW_THETA = np.arctan2(self.FLOW_VY, self.FLOW_VX)
        self.THETA_LIST = [np.pi/2, -np.pi/2, 0, np.pi]

        # generate state transition probabilities
        for i in range(self.num_cells):
            for j in range(self.num_actions):

                # north, strong north - action 0 and action 4
                if j in [0, 4]:
                    if i - self.grid_size[1] < 0:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i-self.grid_size[1]
                                     ] = Decimal(str(1))

                # south, strong south - action 1 and action 5
                elif j in [1, 5]:
                    if i + self.grid_size[1] >= self.num_cells:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i+self.grid_size[1]
                                     ] = Decimal(str(1))

                # east, strong east - action 2 and action 6
                elif j in [2, 6]:
                    if i % self.grid_size[1] == self.grid_size[1]-1:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i+1] = Decimal(str(1))

                # west, strong west - action 3 and action 7
                elif j in [3, 7]:
                    if i % self.grid_size[1] == 0:
                        self.agent_P[i, j, i] = Decimal(str(1))
                    else:
                        self.agent_P[i, j, i-1] = Decimal(str(1))

                if not ((i - self.grid_size[1] < 0) or
                        (i + self.grid_size[1] >= self.num_cells) or
                        (i % self.grid_size[1] == self.grid_size[1]-1) or
                        (i % self.grid_size[1] == 0)):

                    # generate stochastic dynamics for weak actions 
                    if j in [0, 1, 2, 3]:
                        self.agent_P[i, j, :] = self._generate(i, j)
                        
        # initialize agent and environment
        self.reset(self.init_state)
        self._add_reloads()


    def _generate(self, s, a):
        '''
        Given state and action, generate the transition probability array and
        the reload states for weak actions.
        '''
        # combined actual heading
        actual_x = self.AGENT_V*np.cos(self.THETA_LIST[a]) + self.FLOW_MAG[s,a]*np.cos(self.FLOW_THETA[s, a])
        actual_y = self.AGENT_V*np.sin(self.THETA_LIST[a]) + self.FLOW_MAG[s,a]*np.sin(self.FLOW_THETA[s, a])
        actual_theta = np.arctan2(actual_y, actual_x)
        rv = norm(actual_theta, self.HEADING_SD)

        # calculate TP
        tp = np.zeros(self.num_cells)
        tp[s-self.grid_size[1]] = p_n = Decimal(str(round(rv.cdf(3*np.pi/4) - rv.cdf(np.pi/4), 3)))
        tp[s+self.grid_size[1]] = p_s = Decimal(str(round(rv.cdf(-np.pi/4) - rv.cdf(-3*np.pi/4), 3)))
        tp[s+1] = p_e = Decimal(str(round(rv.cdf(np.pi/4) - rv.cdf(-np.pi/4), 3)))
        diff = Decimal(str(round(1 - (p_n + p_s + p_e),3)))
        if p_n + p_s + p_e > Decimal(1):
            tp[s-1] = Decimal(str(0))
            tp[s+1] = Decimal(str(round(Decimal(tp[s+1]) - diff,3))) 
        else:
            tp[s-1] = diff
        return tp
    
    
    def update_strategy(self, agent_id, strategy):
        '''
        Update the strategy attribute to the given strategy for the agent
        '''
        self.strategy[agent_id] = strategy
    
            
    def pick_action(self, strategy=None, state=None, energy=None):
        '''
        Given strategy, current state, and current energy level pick the next
        action of all agents and return action array
        '''
        action_array = []
        for agent_id in range(self.num_agents):
        
            state = self.position[agent_id]
            energy = self.agent_energy[agent_id]
            strategy = self.strategy[agent_id]
            if strategy[agent_id] == None:
                raise Exception('Add a strategy for the agent by using env.update_strategy method')
            data_dict = self.strategy[agent_id][state]
            dict_keys = list(data_dict.keys())
            if len(dict_keys) == 0:
                raise Exception('Strategy does not prescribe a safe action at this state. Increase the capacity of the agent.')
            feasible = []
            for value in dict_keys:
                if value <= energy:
                    feasible.append(value)
            action_string = data_dict[max(feasible)]
            agent_action = ast.literal_eval(action_string)[1]
            action_array.append(agent_action)
        return action_array
        

    def step(self, action_array, do_render=0):
        '''
        Given action, function step updates the state of all the agents and returns
        the resultant state array, cap array, and other info
        '''

        for agent_id in range(self.num_agents):
            
            # initialize variables
            done = 0
            if self.agent_energy[agent_id] < self.saction_cost:
                raise Exception('Warning: energy too low to take strong action.')
        
            # verify action input and decide action
            if isinstance(action_array[agent_id], int) and action_array[agent_id] in list(range(self.num_actions)):
                self.position[agent_id] = np.random.choice(self.num_cells,
                                         p=self.agent_P[self.position[agent_id], action_array[agent_id], :])
            else:
                raise Exception('Input action is not a valid action')

            # update energy
            if action_array[agent_id] in [0,1,2,3]:
                self.agent_energy[agent_id] -= self.waction_cost
            else:
                self.agent_energy[agent_id] -= self.saction_cost
            if self.is_reload[self.position[agent_id]]:
                self.agent_energy[agent_id] = self.agent_capacity[agent_id]

            # energy exhaustion check
            if self.agent_energy[agent_id] <= 1 and self.agent_energy[agent_id] >= 0:
                done = 1
       
            # update other terms
            self.states_history[agent_id].append(self.position[agent_id])
            self.actions_history[agent_id].append(action_array[agent_id])

     
        self.time_steps += 1 
        
        # render and return
        if do_render == 1:
            self.render_grid()
        info = (self.position, action_array, self.agent_energy, done)
        return info
    

    def reset(self, init_state=None):

        # random initial position
        for agent_id in range(self.num_agents):
            if init_state == None:
                self.position[agent_id] = np.random.randint(self.num_cells)
            else:
                if 0 <= init_state[agent_id] < self.num_cells and isinstance(init_state[agent_id], int):
                    self.position[agent_id] = init_state[agent_id]
                else:
                    raise Exception(
                        'states should be integers between 0 and num_cells. Check init_state again')
                

            self.agent_energy[agent_id] = self.agent_capacity[agent_id]
            self.states_history[agent_id] = [self.position[agent_id]] 
            self.actions_history[agent_id] = []
            self.targets_history[agent_id] = []
        self.time_steps = 0
    

    def _add_reloads(self):    
        """
        Internal method to assign reload states.
        """        
        for state in self.reload_list:
            self.is_reload[state] = 1
            
        
    def _get_dist(self, mdp, state, action):
        """
        Internal method that returns a dictionary of states with nonzero probabilities for
        a given state and action
        """
        dist = dict()
        agent_dist = self.agent_P[state, action, :]
        agent_posstates = [] 
        for i in agent_dist.nonzero()[0]:
            agent_posstates.append(i)
        for i in list(agent_posstates):
            prob = agent_dist[i]
            dist[i] = prob
        return dist
    
    
    def create_consmdp(self):
        """
        Method to export the UUV gridworld and target states into a pre-defined
        standard consMDP form. Returns MDP object and the target set.
        """
        mdp = consMDP.ConsMDP()
    
        # Add states
        for i in range(self.num_cells):
            if self.is_reload[i]:
                mdp.new_state(True, str(i))  # (reload, label)
            else:
                mdp.new_state(False, str(i))
                
        # List all possible states and actions
        states_list = []
        for i in range(self.num_cells):
                states_list.append(i)
            
        actions_list = []
        for i in range(self.num_actions):
                actions_list.append(i)        

        # Extract and add actions to the MDP
        actions = dict()
        for state in states_list:
            for action in actions_list:
                action_label = str([state,action])
                dist = self._get_dist(mdp, state, action)
                if action in [0,1,2,3]: # weak action
                    actions[action_label] = {"from":str(state), "cons":self.waction_cost, "dist":dist}
                else: # strong action
                    actions[action_label] = {"from":str(state), "cons":self.saction_cost, "dist":dist}
                
        for label, act in actions.items():
            fr = mdp.state_with_name(act["from"])
            mdp.add_action(fr, act["dist"], label, act["cons"])
        
        self.consmdp = mdp
    
    
    def get_consmdp(self):
        """
        Method that returns the consMDP object and target set that already exists
        or generates it if it does not exist
        """
        
        if self.consmdp == None:
            self.create_consmdp()
            return (self.consmdp, self.targets_list)
        else:
            return (self.consmdp, self.targets_list)

    
    def _states_to_colors(self):
        '''
        Assign colors to the cells based on their current identity.
        '''
      
        # Define colors
        # 0: light blue; 1 : light gray; 2 : dark gray; 3 : green; 4 : orange; 5: dark blue
        COLORS = {0:np.array([0.85,1.0,1.0]), 1:np.array([0.54,0.54,0.54]), \
                  2:np.array([0.42,0.42,0.42]), 3:np.array([0.0,1.0,0.0]), \
                      4:np.array([1.0,0.37,0.008]), 5:np.array([0.0,0.0,1.0])}
          
        COLORS_TRAJEC = {0:np.array([0.45,0.45,0.45]), 1:np.array([0.71,0.71,0.71]), 2:np.array([0.32,0.32,0.32])}
        
        # 0: light blue; 1 : light gray; 2 : dark gray; 3 : green; 4 : orange; 5: dark blue
        data = np.zeros([self.grid_size[0],self.grid_size[1],3],dtype=np.float32)
        data[:] = COLORS[0] # baseline state color
        
        for agent_id in range(self.num_agents):
            for cell in self.states_history[agent_id]:
                data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS_TRAJEC[agent_id] # history
        for cell in self.targets_all:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[3] # targets
        for cell in self.reload_list:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[4] # reloads
            
        for agent_id in range(self.num_agents):
            data[self.position[agent_id]//self.grid_size[1], self.position[agent_id]%self.grid_size[1]] = COLORS_TRAJEC[agent_id] # current state
        data[self.init_state[0]//self.grid_size[1], self.init_state[0]%self.grid_size[1]] = COLORS[5] # home/base
                
        return data


    def render_grid(self):
        
        img_data = self._states_to_colors()
        fig, ax = plt.subplots()
        ax.axis('off')
        plt.title("Agents Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
        plt.imshow(img_data) 
        plt.show()


    def animate_strategy(self, strategy=None, num_steps=100, interval=100):
        '''
        Run the strategy and animate for num_steps no.of time steps
        '''
        
        if strategy != None:
            self.strategy = strategy
        self.reset(self.init_state)
        fig = plt.figure()
        ax = fig.gca()
        ax.axis('off')
        im = plt.imshow(self._states_to_colors(), animated=True)
        plt.close()
        
        def updatefig(frame_count):
            
            if frame_count == 0:
                im.set_array(self._states_to_colors())
                ax.set_title("Agents Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
                return im
            self.step(self.pick_action())
            im.set_array(self._states_to_colors())
            ax.set_title("Agents Energy: {}, Time Steps: {}".format(self.agent_energy, self.time_steps))
            return im
        return animation.FuncAnimation(fig, updatefig, frames=num_steps, interval=interval)
        
    def _repr_png_(self):
        '''
        Show graphical representation in notebooks.
        '''
        return self.render_grid()
