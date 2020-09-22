"""
Gridworld modeling motion of a constant horizontal velocity UUV in waters
with ocean currents.
"""

# import required packages
import copy
import numpy as np
from fimdp import consMDP
from decimal import Decimal
from matplotlib import pyplot as plt
from scipy.stats import vonmises
import matplotlib.animation as animation


class SingleAgentEnv:

    def __init__(self, grid_size, capacity, reload, target, init_state=None, enhanced_actionspace=0, velocity=5, heading_sd=0.524, weakaction_cost=1, strongaction_cost=2):
        """Class that models a Markov Decision Process where the agent and the environment model the dynamics of a UUV and
        the ocean currents it is operating in.
        """

        # user inputs and other required constants
        self.grid_size = grid_size
        self.capacity = capacity
        self.waction_cost = weakaction_cost
        self.saction_cost = strongaction_cost
        self.reload = reload
        self.target = target
        self.init_state = init_state
        self.position = None
        self.strategy = None
        self.consmdp = None
        self.state_history = []
        self.action_history = []
        self.target_history = []
        self.num_timesteps = 0

        # initialize required variables
        self.num_states = grid_size[0]*grid_size[1]
        if enhanced_actionspace == 0:
            self.num_actions = 8
            self.weak_actions = [0,1,2,3]
            self.strong_actions = [4,5,6,7]
        elif enhanced_actionspace == 1:
            self.num_actions = 16
            self.weak_actions = [0,1,2,3,8,9,10,11]
            self.strong_actions = [4,5,6,7,12,13,14,15]
        self.is_reload = np.zeros(self.num_states)
        self.energy = copy.deepcopy(self.capacity)
        self.trans_prob = np.zeros([self.num_states, self.num_actions, self.num_states])
        self.action_to_label = {0:'Weak East', 1:'Weak North', 2:'Weak West',
                               3:'Weak South', 4:'Strong East', 5:'Strong North',
                               6:'Strong West', 7:'Strong South', 8:'Weak North-East',
                               9: 'Weak North-West', 10:'Weak South-West',
                               11:'Weak South-East', 12:'Strong North-East',
                               13:'Strong North-West', 14:'Strong South-West',
                               15:'Strong South-East'}
        self.label_to_action = {v: k for k, v in self.action_to_label.items()}

        # initialize and generate ocean current flow field
        self.agent_v = velocity
        self.agent_headingsd = heading_sd
        self.flow_vx = 0.1*self.agent_v * np.ones([self.num_states])
        self.flow_vy = 0.2*self.agent_v * np.ones([self.num_states])
        self.flow_mag = np.sqrt([i**2 + j**2 for i,j in zip(self.flow_vx, self.flow_vy)])
        np.linalg.norm([self.flow_vx, self.flow_vy])
        self.flow_theta = np.arctan2(self.flow_vy, self.flow_vx)
        self.action_theta = {0:0, 1:np.pi/2, 2:np.pi, 3:-np.pi/2, 8:np.pi/4,
                           9:3*np.pi/4, 10:-3*np.pi/4, 11:-np.pi/2}

        # generate state transition probabilities
        self.trans_prob = self._generate_dynamics()

        # initialize agent and environment
        self.reset(self.init_state)
        self._add_reloads()

    def _generate_dynamics(self):

        """
        Generate and return the state transition probability array for the given
        gridworld depending on the cardinality of the action space.
        """

        for i in range(self.num_states):
            for j in range(self.num_actions):
                if j in [2, 6]:
                    if (i % self.grid_size[1] == self.grid_size[1]-1):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i+1] = Decimal(str(1))
                elif j in [0, 4]:
                    if (i - self.grid_size[1] < 0):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i-self.grid_size[1]] = Decimal(str(1))
                elif j in [3, 7]:
                    if (i % self.grid_size[1] == 0):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i-1] = Decimal(str(1))
                elif j in [1, 5]:
                    if (i + self.grid_size[1] >= self.num_states):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i+self.grid_size[1]] = Decimal(str(1))

                if self.num_actions == 16:
                    if j in [8, 12]:
                        if (i - self.grid_size[1] < 0) or (i % self.grid_size[1] == self.grid_size[1]-1):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i-self.grid_size[1]+1] = Decimal(str(1))
                    elif j in [9, 13]:
                        if (i - self.grid_size[1] < 0) or (i % self.grid_size[1] == 0):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i-self.grid_size[1]-1] = Decimal(str(1))
                    elif j in [10, 14]:
                        if (i + self.grid_size[1] >= self.num_states) or (i % self.grid_size[1] == 0):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i+self.grid_size[1]-1] = Decimal(str(1))
                    elif j in [11, 15]:
                        if (i + self.grid_size[1] >= self.num_states) or (i % self.grid_size[1] == self.grid_size[1]-1):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i+self.grid_size[1]+1] = Decimal(str(1))

                # generate stochasic dynamics for weak actions
                if not ((i - self.grid_size[1] < 0) or
                        (i + self.grid_size[1] >= self.num_states) or
                        (i % self.grid_size[1] == self.grid_size[1]-1) or
                        (i % self.grid_size[1] == 0)):

                    if j in self.weak_actions:
                        self.trans_prob[i, j, :] = self._generate_stochastic_dynamics(i, j)

        return self.trans_prob


    def _generate_stochastic_dynamics(self, s, a):
        '''
        Given state and action, generate an array listing the probability of the
        agent reaching all the states for the given weak action.
        '''
        # combined actual heading
        actual_vx = self.agent_v*np.cos(self.action_theta[a]) + self.flow_mag[s]*np.cos(self.flow_theta[s])
        actual_vy = self.agent_v*np.sin(self.action_theta[a]) + self.flow_mag[s]*np.sin(self.flow_theta[s])
        actual_theta = np.arctan2(actual_vy, actual_vx)
        rv = vonmises(1/self.agent_headingsd, actual_theta)

        tp = np.zeros(self.num_states)

        if self.num_actions == 8:
            tp[s+1] = Decimal(str(round((rv.cdf(0.25*np.pi) - rv.cdf(-0.25*np.pi)),2)))
            tp[s-self.grid_size[1]] = Decimal(str(round(rv.cdf(0.75*np.pi) - rv.cdf(0.25*np.pi),2)))
            tp[s-1] = Decimal(str(round(rv.cdf(np.pi) - rv.cdf(0.75*np.pi) + rv.cdf(-0.75*np.pi) - rv.cdf(-np.pi),2)))
            tp[s+self.grid_size[1]] =  Decimal(str(1.0)) - Decimal(str(np.sum(copy.deepcopy(tp))))
            tp = tp.round(2)

        elif self.num_actions == 16:
            tp[s+1] = Decimal(str(round(rv.cdf(0.125*np.pi) - rv.cdf(-0.125*np.pi),2)))
            tp[s-self.grid_size[1]] = Decimal(str(round(rv.cdf(0.625*np.pi) - rv.cdf(0.375*np.pi),2)))
            tp[s-1] = Decimal(str(round(rv.cdf(np.pi) - rv.cdf(0.875*np.pi) + rv.cdf(-0.875*np.pi) - rv.cdf(-np.pi),2)))
            tp[s+self.grid_size[1]] = Decimal(str(round(rv.cdf(-0.375*np.pi) - rv.cdf(-0.625*np.pi),2)))
            tp[s-self.grid_size[1]+1] = Decimal(str(round(rv.cdf(0.375*np.pi) - rv.cdf(0.125*np.pi),2)))
            tp[s-self.grid_size[1]-1] = Decimal(str(round(rv.cdf(0.875*np.pi) - rv.cdf(0.625*np.pi),2)))
            tp[s+self.grid_size[1]-1] = Decimal(str(round(rv.cdf(-0.625*np.pi) - rv.cdf(-0.875*np.pi),2)))
            tp[s+self.grid_size[1]+1] =  Decimal(str(1.0)) - Decimal(str(np.sum(copy.deepcopy(tp))))
            tp = tp.round(2)
        else:
            raise Exception('Invalid number of actions. Only two configurations possible')

        if (not np.all(tp>=0)) or (abs(np.sum(tp) - 1.0) >=  1e-8):
            print(tp)
            raise Exception('Invalid distribution for state {} and action {}'.format(s,a))
        else:
            return tp

    def update_strategy(self, strategy):
        '''
        Update the strategy attribute to the given strategy
        '''
        self.strategy = strategy


    def pick_action(self, strategy=None, state=None, energy=None):
        '''
        Pick the next action of the agent given strategy, current state,
        and current energy level.
        '''
        if state==None:
            state = self.position
        if energy==None:
            energy = self.energy
        if strategy==None:
            strategy = self.strategy
            if self.strategy == None:
                raise Exception('Add a strategy to the agent by using env.update_strategy method')
        data_dict = self.strategy[state]
        dict_keys = list(data_dict.keys())
        if len(dict_keys) == 0:
            raise Exception('Strategy does not prescribe a safe action at this state. Increase the capacity of the agent.')
        feasible = []
        for value in dict_keys:
            if value <= energy:
                feasible.append(value)
        if len(feasible) == 0:
                raise Exception('Strategy does not prescribe a safe action at this energy level. Increase the capacity of the agent.')
        action_string = data_dict[max(feasible)]
        action = self.label_to_action[action_string]
        return action

    def step(self, action, do_render=0):
        """
        Update the state and energy of an agent given the action and return
        the resultant state, energy level, and other info. Returns done == 1 if
        the energy of the agent is exhausted.
        """

        # initialize variables
        done = 0
        if self.energy < self.saction_cost:
            raise Exception('Warning: energy too low to take a strong action.')

        # verify action input and decide
        if isinstance(action, int) and action in list(range(self.num_actions)):
            self.position = np.random.choice(self.num_states,
                                             p=self.trans_prob[self.position, action, :])
        else:
            raise Exception('Input action is not a valid action')

        # update energy
        if action in self.weak_actions:
            self.energy -= self.waction_cost
        elif action in self.strong_actions:
            self.energy -= self.saction_cost
        if self.is_reload[self.position]:
            self.energy = self.capacity

        # energy exhaustion check
        if self.energy < self.waction_cost:
            done = 1
        elif self.energy < 0:
            raise Exception('Agent energy cannot be negative')

        # update and render
        self.state_history.append(self.position)
        self.action_history.append(action)
        self.num_timesteps += 1
        if do_render == 1:
            self.render_grid()
        info = (self.position, action, self.energy, done)
        return info

    def reset(self, init_state=None, reset_energy=None):
        """
        Reset the position of the agent to init_state (if given) or to a randomly
        selected state in the state space. Also resets the energy to the capacity
        of thr agent and clears any stored data.
        """

        if init_state == None:
            self.position = np.random.randint(self.num_states)
        else:
            if 0 <= init_state < self.num_states and isinstance(init_state, int):
                self.position = init_state
            else:
                raise Exception('states should be integers between 0 and num_states. Check init_state again')
        if reset_energy == None:
            self.energy = copy.deepcopy(self.capacity)
        else:
            if isinstance(reset_energy, int) and reset_energy >= self.saction_cost:
                self.energy = reset_energy
            else:
                raise Exception('The choice of reset energy must be greater than or equal to strong action cost')
        self.state_history = [self.position]
        self.action_history = []
        self.target_history = []
        self.num_timesteps = 0


    def _add_reloads(self):
        """
        Assigns reload features to given list of states.
        """
        for state in self.reload:
            self.is_reload[state] = 1

    def _get_dist(self, state, action):
        """
        Returns a dictionary of states with nonzero probabilities for
        a given state and action pair.
        """
        dist = dict()
        agent_dist = self.trans_prob[state, action, :]
        agent_posstates = []
        for i in agent_dist.nonzero()[0]:
            agent_posstates.append(i)
        for i in list(agent_posstates):
            prob = agent_dist[i]
            dist[i] = Decimal(str(round(prob,2)))
        return dist

    def create_consmdp(self):
        """
        Exports the UUV gridworld and target states into a pre-defined
        standard consMDP object which is stored in the consmdp attribute
        """
        mdp = consMDP.ConsMDP()

        # Add states to the consMDP object
        for i in range(self.num_states):
            if self.is_reload[i]:
                mdp.new_state(True, str(i))  # (reload, label)
            else:
                mdp.new_state(False, str(i))

        # Extract and add actions to the consMDP object
        for state in range(self.num_states):
            for action in range(self.num_actions):
                dist = self._get_dist(state, action)
                if action in self.weak_actions:
                    mdp.add_action(mdp.state_with_name(str(state)), dist, self.action_to_label[action], self.waction_cost)
                elif action in self.strong_actions:
                    mdp.add_action(mdp.state_with_name(str(state)), dist, self.action_to_label[action], self.saction_cost)
        self.consmdp = mdp

    def get_consmdp(self):
        """
        Returns the consMDP object and target set that already exists
        or generates the consMDP object if it does not exist and then returns it.
        """

        if self.consmdp == None:
            self.create_consmdp()
            return (self.consmdp, self.target)
        else:
            return (self.consmdp, self.target)

    def _states_to_colors(self):
        '''
        Assigns colors to the cells based on their current identity for visualization
        of the environment and animation of a given policy
        '''

        # Define colors
        # 0: light blue; 1 : light gray; 2 : dark gray; 3 : green; 4 : orange; 5: dark blue
        COLORS = {0:np.array([0.85,1.0,1.0]), 1:np.array([0.54,0.54,0.54]), \
                  2:np.array([0.42,0.42,0.42]), 3:np.array([0.0,1.0,0.0]), \
                      4:np.array([1.0,0.37,0.008]), 5:np.array([0.0,0.0,1.0])}

        data = np.zeros([self.grid_size[0],self.grid_size[1],3],dtype=np.float32)
        data[:] = COLORS[0] # baseline state color
        for cell in self.state_history:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[2] # history
        for cell in self.target:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[3] # targets
        for cell in self.reload:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[4] # reloads
        data[self.position//self.grid_size[1], self.position%self.grid_size[1]] = COLORS[5] # current state
        return data

    def render_grid(self):
        """
        Renders the current state of the environment
        """

        img_data = self._states_to_colors()
        fig, ax = plt.subplots()
        ax.axis('off')
        plt.title("Energy: {}, Time Steps: {}".format(self.energy, self.num_timesteps))
        plt.imshow(img_data)
        plt.show()

    def animate_strategy(self, strategy=None, num_steps=100, interval=100):
        """
        Executes the strategy for num_steps no.of time steps and animates the
        resultant trajectory.
        """

        if strategy != None:
            self.strategy = strategy
            if self.strategy == None:
                raise Exception('No strategy object assigned to the agent. Use self.update_strategy() method to assign a strategy to the agent.')
        self.reset(self.init_state)
        fig = plt.figure()
        ax = fig.gca()
        ax.axis('off')
        im = plt.imshow(self._states_to_colors(), animated=True)
        plt.close()

        def updatefig(frame_count):

            if frame_count == 0:
                im.set_array(self._states_to_colors())
                ax.set_title("Energy: {}, Time Steps: {}".format(self.energy, self.num_timesteps))
                return im
            self.step(self.pick_action())
            im.set_array(self._states_to_colors())
            ax.set_title("Energy: {}, Time Steps: {}".format(self.energy, self.num_timesteps))
            return im
        return animation.FuncAnimation(fig, updatefig, frames=num_steps, interval=interval)

    def _repr_png_(self):
        '''
        Show graphical representation in notebooks.
        '''
        return self.render_grid()

class SynchronousMultiAgentEnv:

    def __init__(self, num_agents, grid_size, capacity, reload, target, init_state=None, enhanced_actionspace=0, velocity=5, heading_sd=0.524, weakaction_cost=1, strongaction_cost=2):
        """Class that models a Markov Decision Process where the agents and the environment model the dynamics of multiple UUV and
        the ocean currents it is operating in. All transitions in the environment are synchronous.
        """

        # user inputs and other required constants
        self.num_agents = num_agents
        self.grid_size = grid_size
        self.capacity = capacity
        self.waction_cost = weakaction_cost
        self.saction_cost = strongaction_cost
        self.reload = reload
        self.target = target
        self.target_allocation = [[] for i in range(self.num_agents)]
        self.init_state = init_state
        self.position = [None for i in range(self.num_agents)]
        self.strategy = [None for i in range(self.num_agents)]
        self.agent_done = [0 for i in range(self.num_agents)]
        self.consmdp = None
        self.state_history = [[] for i in range(self.num_agents)]
        self.action_history = [[] for i in range(self.num_agents)]
        self.target_history = [[] for i in range(self.num_agents)]
        self.num_timesteps = 0

        # initialize required variables
        self.num_states = grid_size[0]*grid_size[1]
        if enhanced_actionspace == 0:
            self.num_actions = 8
            self.weak_actions = [0,1,2,3]
            self.strong_actions = [4,5,6,7]
        elif enhanced_actionspace == 1:
            self.num_actions = 16
            self.weak_actions = [0,1,2,3,8,9,10,11]
            self.strong_actions = [4,5,6,7,12,13,14,15]
        self.is_reload = np.zeros(self.num_states)
        self.energy = copy.deepcopy(self.capacity)
        self.trans_prob = np.zeros([self.num_states, self.num_actions, self.num_states])
        self.action_to_label = {0:'Weak East', 1:'Weak North', 2:'Weak West',
                               3:'Weak South', 4:'Strong East', 5:'Strong North',
                               6:'Strong West', 7:'Strong South', 8:'Weak North-East',
                               9: 'Weak North-West', 10:'Weak South-West',
                               11:'Weak South-East', 12:'Strong North-East',
                               13:'Strong North-West', 14:'Strong South-West',
                               15:'Strong South-East'}
        self.label_to_action = {v: k for k, v in self.action_to_label.items()}

        # initialize and generate ocean current flow field
        self.agent_v = velocity
        self.agent_headingsd = heading_sd
        self.flow_vx = 0.1*self.agent_v * np.ones([self.num_states])
        self.flow_vy = 0.2*self.agent_v * np.ones([self.num_states])
        self.flow_mag = np.sqrt([i**2 + j**2 for i,j in zip(self.flow_vx, self.flow_vy)])
        np.linalg.norm([self.flow_vx, self.flow_vy])
        self.flow_theta = np.arctan2(self.flow_vy, self.flow_vx)
        self.action_theta = {0:0, 1:np.pi/2, 2:np.pi, 3:-np.pi/2, 8:np.pi/4,
                           9:3*np.pi/4, 10:-3*np.pi/4, 11:-np.pi/2}

        # generate state transition probabilities
        self.trans_prob = self._generate_dynamics()

        # initialize agent and environment
        self.reset(self.init_state)
        self._add_reloads()

    def _generate_dynamics(self):

        """
        Generate and return the state transition probability array for the given
        gridworld depending on the cardinality of the action space.
        """

        for i in range(self.num_states):
            for j in range(self.num_actions):
                if j in [2, 6]:
                    if (i % self.grid_size[1] == self.grid_size[1]-1):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i+1] = Decimal(str(1))
                elif j in [0, 4]:
                    if (i - self.grid_size[1] < 0):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i-self.grid_size[1]] = Decimal(str(1))
                elif j in [3, 7]:
                    if (i % self.grid_size[1] == 0):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i-1] = Decimal(str(1))
                elif j in [1, 5]:
                    if (i + self.grid_size[1] >= self.num_states):
                        self.trans_prob[i, j, i] = Decimal(str(1))
                    else:
                        self.trans_prob[i, j, i+self.grid_size[1]] = Decimal(str(1))

                if self.num_actions == 16:
                    if j in [8, 12]:
                        if (i - self.grid_size[1] < 0) or (i % self.grid_size[1] == self.grid_size[1]-1):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i-self.grid_size[1]+1] = Decimal(str(1))
                    elif j in [9, 13]:
                        if (i - self.grid_size[1] < 0) or (i % self.grid_size[1] == 0):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i-self.grid_size[1]-1] = Decimal(str(1))
                    elif j in [10, 14]:
                        if (i + self.grid_size[1] >= self.num_states) or (i % self.grid_size[1] == 0):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i+self.grid_size[1]-1] = Decimal(str(1))
                    elif j in [11, 15]:
                        if (i + self.grid_size[1] >= self.num_states) or (i % self.grid_size[1] == self.grid_size[1]-1):
                            self.trans_prob[i, j, i] = Decimal(str(1))
                        else:
                            self.trans_prob[i, j, i+self.grid_size[1]+1] = Decimal(str(1))

                # generate stochasic dynamics for weak actions
                if not ((i - self.grid_size[1] < 0) or
                        (i + self.grid_size[1] >= self.num_states) or
                        (i % self.grid_size[1] == self.grid_size[1]-1) or
                        (i % self.grid_size[1] == 0)):

                    if j in self.weak_actions:
                        self.trans_prob[i, j, :] = self._generate_stochastic_dynamics(i, j)

        return self.trans_prob


    def _generate_stochastic_dynamics(self, s, a):
        """
        Given state and action, generate an array listing the probability of the
        agent reaching all the states for the given weak action.
        """
        # combined actual heading
        actual_vx = self.agent_v*np.cos(self.action_theta[a]) + self.flow_mag[s]*np.cos(self.flow_theta[s])
        actual_vy = self.agent_v*np.sin(self.action_theta[a]) + self.flow_mag[s]*np.sin(self.flow_theta[s])
        actual_theta = np.arctan2(actual_vy, actual_vx)
        rv = vonmises(1/self.agent_headingsd, actual_theta)

        tp = np.zeros(self.num_states)

        if self.num_actions == 8:
            tp[s+1] = Decimal(str(round((rv.cdf(0.25*np.pi) - rv.cdf(-0.25*np.pi)),2)))
            tp[s-self.grid_size[1]] = Decimal(str(round(rv.cdf(0.75*np.pi) - rv.cdf(0.25*np.pi),2)))
            tp[s-1] = Decimal(str(round(rv.cdf(np.pi) - rv.cdf(0.75*np.pi) + rv.cdf(-0.75*np.pi) - rv.cdf(-np.pi),2)))
            tp[s+self.grid_size[1]] =  Decimal(str(1.0)) - Decimal(str(np.sum(copy.deepcopy(tp))))
            tp = tp.round(2)

        elif self.num_actions == 16:
            tp[s+1] = Decimal(str(round(rv.cdf(0.125*np.pi) - rv.cdf(-0.125*np.pi),2)))
            tp[s-self.grid_size[1]] = Decimal(str(round(rv.cdf(0.625*np.pi) - rv.cdf(0.375*np.pi),2)))
            tp[s-1] = Decimal(str(round(rv.cdf(np.pi) - rv.cdf(0.875*np.pi) + rv.cdf(-0.875*np.pi) - rv.cdf(-np.pi),2)))
            tp[s+self.grid_size[1]] = Decimal(str(round(rv.cdf(-0.375*np.pi) - rv.cdf(-0.625*np.pi),2)))
            tp[s-self.grid_size[1]+1] = Decimal(str(round(rv.cdf(0.375*np.pi) - rv.cdf(0.125*np.pi),2)))
            tp[s-self.grid_size[1]-1] = Decimal(str(round(rv.cdf(0.875*np.pi) - rv.cdf(0.625*np.pi),2)))
            tp[s+self.grid_size[1]-1] = Decimal(str(round(rv.cdf(-0.625*np.pi) - rv.cdf(-0.875*np.pi),2)))
            tp[s+self.grid_size[1]+1] =  Decimal(str(1.0)) - Decimal(str(np.sum(copy.deepcopy(tp))))
            tp = tp.round(2)
        else:
            raise Exception('Invalid number of actions. Only two configurations possible')

        if (not np.all(tp>=0)) or (abs(np.sum(tp) - 1.0) >=  1e-8):
            print(tp)
            raise Exception('Invalid distribution for state {} and action {}'.format(s,a))
        else:
            return tp

    def update_strategy(self, agent_id, strategy):
        '''
        Update the strategy attribute of a specified agent to the given strategy
        '''
        self.strategy[agent_id] = strategy

    def pick_action(self, strategy=None, state=None, energy=None):
        """
        Given strategy, current state, and current energy level pick the next
        action of all agents and return action array
        """
        if state==None:
            state = self.position
        if energy==None:
                energy = self.energy
        if strategy==None:
            strategy=self.strategy

        action_array = []
        for agent_id in range(self.num_agents):
            if self.agent_done[agent_id] == 1:
                action_array.append(-1)
            else:
                state = self.position[agent_id]
                energy = self.energy[agent_id]
                strategy = self.strategy[agent_id]
                if strategy[agent_id] == None:
                    raise Exception('Add a strategy for the agent {} by using env.update_strategy method'.format(agent_id))
                data_dict = self.strategy[agent_id][state]
                dict_keys = list(data_dict.keys())
                if len(dict_keys) == 0:
                    raise Exception('Strategy does not prescribe a safe action at this state. Increase the capacity of the agent.')
                feasible = []
                for value in dict_keys:
                    if value <= energy:
                        feasible.append(value)
                if len(feasible) == 0:
                    raise Exception('Strategy does not prescribe a safe action at this energy level. Increase the capacity of the agent.')
                action_string = data_dict[max(feasible)]
                action = self.label_to_action[action_string]
                action_array.append(action)
        return action_array

    def step(self, action, do_render=0):
        """
        Update the state and energy of all the agents given the action and return
        the resultant state, energy level, and other info. Returns done to show the
        status of different agents
        """

        done = [0 for i in range(self.num_agents)]
        for agent_id in range(self.num_agents):
            if action[agent_id] == -1:
                done[agent_id] == 1
                continue
            else:
                # initialize variables
                if self.energy[agent_id] < self.saction_cost:
                    raise Exception('Warning: Current energy ({}) for agent {} too low to take strong action.'.format(self.energy[agent_id], agent_id))

                # verify action input and decide
                if isinstance(action[agent_id], int) and action[agent_id] in list(range(self.num_actions)):
                    self.position[agent_id] = np.random.choice(self.num_states,
                                                p=self.trans_prob[self.position[agent_id], action[agent_id], :])
                else:
                    raise Exception('Input action is not a valid action')

                # update energy
                if action[agent_id] in self.weak_actions:
                    self.energy[agent_id] -= self.waction_cost
                elif action[agent_id] in self.strong_actions:
                    self.energy[agent_id] -= self.saction_cost
                if self.is_reload[self.position[agent_id]]:
                    self.energy[agent_id] = self.capacity[agent_id]

                # energy exhaustion check
                if self.energy[agent_id] < self.waction_cost:
                    done[agent_id] = 1
                elif self.energy[agent_id] < 0:
                    raise Exception('Agent energy cannot be negative')

            # update and render
            self.state_history[agent_id].append(self.position[agent_id])
            self.action_history[agent_id].append(action[agent_id])
        self.num_timesteps += 1
        if do_render == 1:
            self.render_grid()
        info = (self.position, action, self.energy, done)
        return info

    def reset(self, init_state=None, reset_energy=None):
        """
        Reset the position of the agents to init_states (if given) or to randomly
        selected states in the state space. Also resets the energy to the capacity
        of the agents and clears any stored data.
        """

        for agent_id in range(self.num_agents):
            if init_state == None:
                self.position[agent_id] =  np.random.randint(self.num_states)
            else:
                if 0 <= init_state[agent_id] < self.num_states and isinstance(init_state[agent_id], int):
                    self.position[agent_id] = init_state[agent_id]
                else:
                    raise Exception('states should be integers between 0 and num_states. Check init_state again')

            if reset_energy == None:
                self.energy[agent_id] = self.capacity[agent_id]
            else:
                self.energy[agent_id] = reset_energy[agent_id]
            self.state_history[agent_id] = []
            self.action_history[agent_id] = []
            self.target_history[agent_id] = []
            self.agent_done[agent_id] = 0
        self.num_timesteps = 0

    def _add_reloads(self):
        """
        Assigns reload features to given list of states.
        """
        for state in self.reload:
            self.is_reload[state] = 1

    def _get_dist(self, state, action):
        """
        Returns a dictionary of states with nonzero probabilities for
        a given state and action pair.
        """
        dist = dict()
        agent_dist = self.trans_prob[state, action, :]
        agent_posstates = []
        for i in agent_dist.nonzero()[0]:
            agent_posstates.append(i)
        for i in list(agent_posstates):
            prob = agent_dist[i]
            dist[i] = Decimal(str(round(prob,2)))
        return dist

    def create_consmdp(self):
        """
        Exports the UUV gridworld and target states into a pre-defined
        standard consMDP object which is stored in the consmdp attribute
        """
        mdp = consMDP.ConsMDP()

        # Add states to the consMDP object
        for i in range(self.num_states):
            if self.is_reload[i]:
                mdp.new_state(True, str(i))  # (reload, label)
            else:
                mdp.new_state(False, str(i))

        # Extract and add actions to the consMDP object
        for state in range(self.num_states):
            for action in range(self.num_actions):
                dist = self._get_dist(state, action)
                if action in self.weak_actions:
                    mdp.add_action(mdp.state_with_name(str(state)), dist, self.action_to_label[action], self.waction_cost)
                elif action in self.strong_actions:
                    mdp.add_action(mdp.state_with_name(str(state)), dist, self.action_to_label[action], self.saction_cost)
        self.consmdp = mdp

    def get_consmdp(self):
        """
        Returns the consMDP object and target set that already exists
        or generates the consMDP object if it does not exist and then returns it.
        """

        if self.consmdp == None:
            self.create_consmdp()
            return (self.consmdp, self.target)
        else:
            return (self.consmdp, self.target)

    def allocate_target(self, allocation_list):
        """
        Assigns given target allocation to different agents and check if the
        allocation is complete
        """
        targets_all = []
        for target_set in allocation_list:
            targets_all += target_set
        if set(targets_all) == set(self.target):
            for agent_id in range(self.num_agents):
                self.target_allocation[agent_id] = allocation_list[agent_id]
        else:
            raise Exception('The given allocation of targets doesnot cover all the targets in the environment')

    def _states_to_colors(self):
        '''
        Assigns colors to the cells based on their current identity for visualization
        of the environment and animation of a given policy
        '''

        # Define colors
        # 0: light blue; 1 : light gray; 2 : dark gray; 3 : green; 4 : orange; 5: dark blue
        COLORS = {0:np.array([0.85,1.0,1.0]), 1:np.array([0.54,0.54,0.54]), \
                  2:np.array([0.42,0.42,0.42]), 3:np.array([0.0,1.0,0.0]), \
                      4:np.array([1.0,0.37,0.008]), 5:np.array([0.0,0.0,1.0])}
        COLORS_TRAJEC = {0:np.array([0.45,0.45,0.45]), 1:np.array([0.71,0.71,0.71]), 2:np.array([0.32,0.32,0.32])}

        data = np.zeros([self.grid_size[0],self.grid_size[1],3],dtype=np.float32)
        data[:] = COLORS[0] # baseline state color
        for agent_id in range(self.num_agents):
            for cell in self.state_history[agent_id]:
                data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS_TRAJEC[agent_id] # history
        for cell in self.target:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[3] # targets
        for cell in self.reload:
            data[cell//self.grid_size[1], cell%self.grid_size[1]] = COLORS[4] # reloads

        for agent_id in range(self.num_agents):
            data[self.position[agent_id]//self.grid_size[1], self.position[agent_id]%self.grid_size[1]] = COLORS_TRAJEC[agent_id] # current state
            data[self.init_state[agent_id]//self.grid_size[1], self.init_state[agent_id]%self.grid_size[1]] = COLORS[5] # home/base
        return data

    def render_grid(self):
        """
        Renders the current state of the environment
        """

        img_data = self._states_to_colors()
        fig, ax = plt.subplots()
        ax.axis('off')
        plt.title("Energy: {}, Time Steps: {}".format(self.energy, self.num_timesteps))
        plt.imshow(img_data)
        plt.show()

    def animate_strategy(self, strategy=None, num_steps=100, interval=100):
        """
        Executes the strategy for num_steps no.of time steps and animates the
        resultant trajectory.
        """

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
                ax.set_title("Energy: {}, Time Steps: {}".format(self.energy, self.num_timesteps))
                return im
            self.step(self.pick_action())
            im.set_array(self._states_to_colors())
            ax.set_title("Energy: {}, Time Steps: {}".format(self.energy, self.num_timesteps))
            return im
        return animation.FuncAnimation(fig, updatefig, frames=num_steps, interval=interval)

    def _repr_png_(self):
        '''
        Show graphical representation in notebooks.
        '''
        return self.render_grid()


