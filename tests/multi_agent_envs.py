# # Test computation of minimal capacity
import fimdp
from reachability_examples import ultimate
from fimdp.energy_solver import AS_REACH
from fimdp.energy_solver import BUCHI

from fimdp.mincap import bin_search
from fimdpenv.MarsEnv import MarsEnv
import matplotlib.pyplot as plt
from networkx.algorithms import tournament
#import MarsEnv
import numpy as np
import scipy.optimize
from scipy.optimize import linear_sum_assignment
import networkx as nx
import math
import multi_agent_codes
from fimdpenv import setup, UUVEnv
from UUVEnv import SynchronousMultiAgentEnv

#from fimdpenv.env_multiagent import setup
#from env_multiagent import visualize_allocation

#from env_multiagent import create_env

def create_multiagent_env():
    """
        :return:
    e: multi-agent UUVEnv
    consmdp: Underlying consumption MDP of the environment
    targets: set of targets
    """
    #env_multiagent setup function
    setup()
    #generate environment
    num_agents=3
    e = SynchronousMultiAgentEnv(num_agents=num_agents, grid_size=[20, 20], capacity=[100, 100, 100], reload=[22, 297],
                                   target=[24, 44, 57, 71, 87, 102, 191, 156, 232, 345], init_state=[350, 178, 65], enhanced_actionspace=0)    #generate consumption MDP
    #generate consumption mdp
    e.create_consmdp()
    consmdp1 = e.get_consmdp()
    consmdp = consmdp1[0]
    #generate targets
    targets = e.target
    #print(targets)
    return e,consmdp,targets,num_agents

def create_costs_for_agents(Agent_graph,consmdp,targets):
    """
    :param Agent_graph: networkx graph of with the list of targets
    :param consmdp: Underlying consumption MDP of the environment
    :param targets: set of targets
    :return:
    Agent_graph: updated networkx graph with the list of targets and capacities
    """
    for item in targets:
        for item2 in targets:
            if not item==item2:
                #compute the capacity by bin_search
                result = bin_search(consmdp, item, item2)

                #add the edge with capacity
                Agent_graph.add_edge(item, item2, weight=result)

    return Agent_graph

if __name__ == "__main__":
    #create multi agent env
    env,MDP,T,num_agent=create_multiagent_env()
    #print(MDP,T)
    #generate networkx graph
    Graph=multi_agent_codes.generate_Graph(T)
    #generate capacities
    Graph_cost=create_costs_for_agents(Graph,MDP,T)
    #print(Graph_cost)
    #generate minimum spanning tree
    Tree=multi_agent_codes.generate_minimumspanning_tree(Graph_cost)
    #print(Tree)
    #generate approximate hamiltonian path
    hamilton_path=multi_agent_codes.min_hamilton(Tree)
    #print(hamilton_path)
    #compute cost of the path
    cost=multi_agent_codes.compute_cost(Graph_cost,hamilton_path)
    #print(cost)
    #assign paths to the agents
    agent_lists,cost_bisec=multi_agent_codes.bisection_loop(Graph_cost,hamilton_path,num_agent)
    print("Showing the allocation for agents")
    print(agent_lists)
    #compute the allocation costs
    cost_lists=multi_agent_codes.compute_cost_assignments(Graph_cost,agent_lists)
    print("Printing the costs of the allocations")
    print(cost_lists)
    #visualize_allocation(e)

    #gather allocation list
    allocation_list = agent_lists
    #allocates targets to agents
    env.allocate_target(allocation_list)
    #generate mdp
    consmdp1 = env.get_consmdp()
    mdp = consmdp1[0]
    #energy sovler
    from fimdp.energy_solver import GoalLeaningES
    #compute strategies, pulled from Pranay
    for agent_id in range(env.num_agents):
        solver = GoalLeaningES(mdp, env.capacity[agent_id], env.target_allocation[agent_id], threshold=0.1)
        strategy = solver.get_strategy(fimdp.energy_solver.BUCHI)
        env.update_strategy(agent_id, strategy)
    env.animate_strategy(num_steps=50, interval=100)