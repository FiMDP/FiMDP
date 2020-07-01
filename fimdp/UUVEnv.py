# -*- coding: utf-8 -*-
"""
Gridworld modeling motion of a constant horizontal velocity UUV in waters
with ocean currents.
"""

# import required packages
import time
import numpy as np
import random
from decimal import Decimal
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.stats import norm
import seaborn as sns
from IPython import display

from fimdp import consMDP


class Env:

    def __init__(self, grid_size, agent_velocity, heading_sd, agent_capacity, weakaction_cost, strongaction_cost, reload_list, target_list, init_state=None, render=False):
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
        :param agent_v: Positive number that denotes the constant horizontal velocity of the uuv.
        :type agent_v: float
        :param heading_sd: Positive number that denotes the standard deviation in the true heading of the agent.
        :type heading_sd: float
        :param reload_ratio: Positive number between 0 and 1 that denotes the ratio of number of reload states.
        :type reload_ratio: float
        :param target_ratio: Positive number between 0 and 1 that denotes the ratio of number of target states.
        :type target_ratio: float
        :param init_state: An integer denoting the initial state of the agent, defaults to None
        :type init_state: int, optional
        """

        # User inputs and other required constants
        self.grid_size = grid_size
        self.agent_capacity = agent_capacity
        self.waction_cost = weakaction_cost
        self.saction_cost = strongaction_cost
        self.agent_v = agent_velocity
        self.heading_sd = heading_sd
        self.reload_list = reload_list
        self.target_list = target_list
        self.position = None
        self.target_state = None
        self.states_history = []
        self.count = 0
        self.render = render

        # initialize required variables
        self.num_cells = grid_size[0]*grid_size[1]
        self.is_reload = np.zeros(self.num_cells)
        self.num_actions = 8
        self.state = init_state
        self.agent_energy = self.agent_capacity

        # initialize transition probabilities
        self.agent_P = np.zeros(
            [self.num_cells, self.num_actions, self.num_cells])

        # TODO Generalize current parameters declration and flow generation
        # initialize and generate current flow field -- * DEMO CONFIG ONLY
        self.current_vx = 0.1*self.agent_v * \
            np.ones([self.num_cells, self.num_cells])
        self.current_vy = 0.2*self.agent_v * \
            np.ones([self.num_cells, self.num_cells])
        self.current_mag = np.hypot(self.current_vx, self.current_vy)
        self.current_theta = np.arctan2(self.current_vy, self.current_vx)

        # declare heading for different directions N, S, E, W, SN, SS, SE, SW
        self.list_theta = [np.pi/2, -np.pi/2, 0, np.pi]

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

                    # generate dynamics of non border states for weak actions
                    if j in [0, 1, 2, 3]:
                        self.agent_P[i, j, :] = self._generate(i, j)
                        

        # initialize agent and rover positions and render grid world
        self.reset(init_state)
        self._get_targets_reloads()

    # TODO Generalize reload state generation
    def _generate(self, s, a):
        '''
        Given state and action, generate the transition probability array and
        the reload states for weak actions.
        '''

        # combined actual heading
        actual_x = self.agent_v*np.cos(self.list_theta[a]) + self.current_mag[s,a]*np.cos(self.current_theta[s, a])
        actual_y = self.agent_v*np.sin(self.list_theta[a]) + self.current_mag[s,a]*np.sin(self.current_theta[s, a])
        actual_theta = np.arctan2(actual_y, actual_x)
        rv = norm(actual_theta, self.heading_sd)

        # calculate transition probabailities
        tp = np.zeros(self.num_cells)
        tp[s-self.grid_size[1]] = p_n = Decimal(str(round(rv.cdf(3*np.pi/4) - rv.cdf(np.pi/4), 3)))
        tp[s+self.grid_size[1]] = p_s = Decimal(str(round(rv.cdf(-np.pi/4) - rv.cdf(-3*np.pi/4), 3)))
        tp[s+1] = p_e = Decimal(str(round(rv.cdf(np.pi/4) - rv.cdf(-np.pi/4), 3)))
        
        diff = Decimal(str(1 - (p_n + p_s + p_e)))
        
        if p_n + p_s + p_e > Decimal(1):
            
            tp[s-1] = Decimal(str(0))
            tp[s+1] = Decimal(str(Decimal(tp[s+1]) - diff)) 
            
        else:
            tp[s-1] = diff
            
        return tp

    def step(self, action):
        '''
        Given action, function step updates the state of the agent and returns
        the resultant state, cap, and other info.s
        '''

        # initialize variables
        done = 0
        previous_position = self.position
        self.states_history.append(previous_position)

        # verify action input and decide action
        if isinstance(action, int) and action in list(range(8)):
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
        if self.agent_energy <= 1 and self.agent_energy >= 0:
            done = 1
        elif self.agent_energy < 0:
            raise Exception('The energy of the agent cannot be negative.')

        self._rendering()
        info = (self.position, action, self.agent_energy, done)
        return info

    def reset(self, init_state=None):

        # random initial position
        if init_state == None:
            self.position = np.random.randint(self.num_cells)
        else:
            if 0 <= init_state < self.num_cells and isinstance(init_state, int):
                self.position = init_state
            else:
                raise Exception(
                    'states should be integers between 0 and num_cells. Check init_state again')
        self.agent_energy = self.agent_capacity
        self.states_history = [self.position]

    def _get_targets_reloads(self):    
        """
        Internal method that generates target states and reload states that are well distributed over reachable
        and unreachable states and are a pre-defined proportion of the total no.of states. The set of target states
        and reload states are assumed to be disjoint.
        """        
        
     

        # create target and reload sets
        reload_list = self.reload_list 

        for state in reload_list:
            self.is_reload[state] = 1
        
    def _get_dist(self, mdp, state, action):
        """
        Internal method that returns a dictionary of states with nonzero probabilities for
        a given state and action
        """
        
        # Initialize
        dist = dict()
        agent_dist = self.agent_P[state, action, :]
        agent_posstates = [] 
        for i in agent_dist.nonzero()[0]:
            agent_posstates.append(i)
            
        # Store non-zero transition probabilities
        for i in list(agent_posstates):
            prob = agent_dist[i]
            dist[i] = prob
    
        return dist
    
    def create_consmdp(self):
        """
        Method to export the martian gridworld and target states into a pre-defined
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

        # Get targets
        target_set = set(self.target_list)
        return (mdp, target_set)


    def _rendering(self):

        if self.render:

            data = -3*np.ones([self.grid_size[0],self.grid_size[1]])
            for cell in self.states_history:
                data[cell//self.grid_size[0], cell%self.grid_size[1]] = 3
            data[self.position//self.grid_size[0], self.position%self.grid_size[1]] = -1
            for cell in self.target_list:
                data[cell//self.grid_size[0], cell%self.grid_size[1]] = 1
            for cell in self.reload_list:
                data[cell//self.grid_size[0], cell%self.grid_size[1]] = 0            

            myColors = ['#A9A9A9',(0.7, 0.0, 0.0, 1.0),(0.7, 0.3, 0.0, 1.0), (0.0, 0.8, 0.0, 1.0),'#5C5959']
            cmap = ListedColormap(myColors)
            plt.clf()
            ax = sns.heatmap(data, cmap=cmap, cbar =False, linewidths=.5, linecolor='lightgray')
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
            ax.set_title("Agent motion")
            plt.pause(0.05)
#            plt.savefig("value" + str(self.count) + ".png")
#            self.count += 1