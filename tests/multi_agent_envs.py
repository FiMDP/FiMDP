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
from fimdp.energy_solver import GoalLeaningES


#from fimdpenv.env_multiagent import setup
#from env_multiagent import visualize_allocation

#from env_multiagent import create_env

def create_multiagent_env():
    """
    :return:
    e: multi-agent UUVEnv
    consmdp: Underlying consumption MDP of the environment
    targets: set of targets
    num_agents: number of agents
    init_state: set of initial states
    """
    #env_multiagent setup function
    setup()
    #generate environment
    num_agents=3
    init_state=[350, 178, 65]
    e = SynchronousMultiAgentEnv(num_agents=num_agents, grid_size=[20, 20], capacity=[100, 100, 100], reload=[22, 297],
                                   target=[24, 44, 57, 71, 87, 102, 191, 156, 232, 345], init_state=init_state,
                                 enhanced_actionspace=0)    #generate consumption MDP
    #generate consumption mdp
    e.create_consmdp()
    consmdp1 = e.get_consmdp()
    consmdp = consmdp1[0]
    #generate targets
    targets = e.target
    #print(targets)
    return e,consmdp,targets,num_agents,init_state

def create_costs_for_agents(Agent_graph,consmdp,targets):
    """
    :param Agent_graph: networkx graph of with the list of targets
    :param consmdp: consumption MDP
    :param targets: set of targets
    :return:
    Agent_graph: updated networkx graph with the list of targets and capacities
    """
    for item in targets:
        for item2 in targets:
            if not item==item2:
                #compute the capacity by bin_search
                result = bin_search(consmdp, item, item2)
                #result=np.random.uniform(0,1)
                #print(result,item,item2)
                #add the edge with capacity
                Agent_graph.add_edge(item, item2, weight=result)

    return Agent_graph

def create_costs_for_agents_targets(consmdp,agent_lists,cost_lists,init_state):
    """
    :param consmdp: consumption MDP
    :param agent_lists: assignments to the each agents
    :param cost_lists: list of the cost of each path
    :param init_state: set of initial states
    :return:
    Bottleneckgraph networkx graph between initial states of the agent and initial elements of the targets
    """

    #generate bipartite graph with the set of initial states and initial targets for each agent
    Bottleneckgraph=nx.Graph()
    for i in range(len(init_state)):

        Bottleneckgraph.add_node(init_state[i])
    for j in range(len(agent_lists)):
        if len(agent_lists[j])>=1:
            Bottleneckgraph.add_node(agent_lists[j][0])

    #go over initial agent states and initial targets for each agent
    for i in range(len(init_state)):
        for j in range(len(agent_lists)):
            #if target exists
            if len(agent_lists[j]) >= 1:

                item1=init_state[i]
                item2=agent_lists[j][0]
                #compute the capacity between initial agent states and initial targets
                result = bin_search(consmdp, item1, item2)
                #result=np.random.uniform(0,0.5)
                #print(result,item1,item2)
                #update the cost if the capacity is higher
                if result> cost_lists[j]:
                    Bottleneckgraph.add_edge(item1, item2, weight=result)
                else:
                    Bottleneckgraph.add_edge(item1, item2, weight=cost_lists[j])

    return Bottleneckgraph


if __name__ == "__main__":
    #create multi agent env
    env,MDP,T,num_agent,init_state=create_multiagent_env()
    #print(MDP,T)
    #generate networkx graph
    Graph=multi_agent_codes.generate_Graph(T)
    #generate capacities
    print("Computing capacities with bin search")
    Graph_cost=create_costs_for_agents(Graph,MDP,T)

    #print(Graph_cost)
    #generate minimum spanning tree
    Tree=multi_agent_codes.generate_minimumspanning_tree_edmonds(Graph_cost)
    #print(Tree.edges,"kruskal")
    #generate approximate hamiltonian path
    hamilton_path=multi_agent_codes.min_hamilton(Tree)
    #print(hamilton_path)
    #compute cost of the path
    cost=multi_agent_codes.compute_cost(Graph_cost,hamilton_path)
    #print(cost)
    #assign paths to the agents
    print("Computing bisection for path assignments")

    agent_lists,cost_bisec=multi_agent_codes.bisection_loop(Graph_cost,hamilton_path,num_agent)
    print("Showing the allocation for agents")
    print(agent_lists)
    #compute the allocation costs
    cost_lists=multi_agent_codes.compute_cost_assignments(Graph_cost,agent_lists)
    print("Showing the costs of the allocations")
    print(cost_lists)
    #visualize_allocation(e)
    print("Generating capacities between agents and set of paths with bin search")

    bottleneck_graph=create_costs_for_agents_targets(MDP,agent_lists,cost_lists,init_state)
    #allocates targets to agents
    print("Computing bottleneck assignment")
    matching=multi_agent_codes.bottleneckassignment(bottleneck_graph)
    final_assignments,final_costs=multi_agent_codes.augment_matching(matching,agent_lists,init_state,bottleneck_graph)
    print("Showing the final ordered allocation for agents with initial states")
    print(final_assignments)
    print("Showing the final ordered costs of the allocations")
    print(final_costs)
    env.allocate_target(final_assignments)
    consmdp1 = env.get_consmdp()
    MDP = consmdp1[0]
    #generate targets
    #compute strategies, pulled from Pranay
    for agent_id in range(env.num_agents):
        solver = GoalLeaningES(MDP, env.capacity[agent_id], env.target_allocation[agent_id], threshold=0.1)
        strategy = solver.get_strategy(fimdp.energy_solver.BUCHI)
        env.update_strategy(agent_id, strategy)
    env.animate_strategy(num_steps=50, interval=100)