# # Test computation of minimal capacity

from reachability_examples import ultimate
from fimdp.energy_solver import AS_REACH
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
import fimdpenv.UUVEnv
from fimdpenv.env_multiagent import setup
from env_multiagent import visualize_allocation

from env_multiagent import create_env

def create_multiagent_env(num_agent):
    setup()

    agents_capacities = [200 for _ in range(num_agent)]
    e = create_env(agents_capacities)
    e.create_consmdp()
    #print(e.init_state)
    # print(dir(e))
    # print(e.targets_all)
    # print(e.targets_list)
    consmdp1 = e.get_consmdp()
    # print(consmdp1)
    consmdp = consmdp1[0]
    # print(type(consmdp))
    targets = e.targets_all
    return consmdp,targets

def create_costs_for_agents(Agent_graph,consmdp,targets):


    for item in targets:
        for item2 in targets:
            #print(item,item2)
            if not item==item2:
                result = bin_search(consmdp, item, item2)
                #print(result)

                #for i in range(num_agent):
                    #Agent_graph[i].add_edge(item, item2, weight=result)
                Agent_graph.add_edge(item, item2, weight=result)
    return Agent_graph

num_agent=3
MDP,T=create_multiagent_env(num_agent)
#print(MDP,T)
Graph=multi_agent_codes.generate_Graph(T)
Graph_cost=create_costs_for_agents(Graph,MDP,T)
#print(Graph_cost)
Tree=multi_agent_codes.generate_minimumspanning_tree(Graph_cost)
#print(Tree)
hamilton_path=multi_agent_codes.min_hamilton(Tree)
#print(hamilton_path)

cost=multi_agent_codes.compute_cost(Graph_cost,hamilton_path)
#print(cost)

agent_lists,cost_bisec=multi_agent_codes.bisection_loop(Graph_cost,hamilton_path,num_agent)
print("Showing the allocation for agents")
print(agent_lists)
print("Printing the costs of the allocations")
cost_lists=multi_agent_codes.compute_cost_assignments(Graph_cost,agent_lists)
print(cost_lists)
#visualize_allocation(e)

