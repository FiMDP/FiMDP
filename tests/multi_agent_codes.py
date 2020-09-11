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
# In the following example, the minimal capacity is 15 for Buchi objective defined by the blue states.

#Compute the minimum cost of the assignments by bisection
def compute_min_cost_bisection(Agent_graph,num_agents):
    """
    :param Agent_graph: Networkx graph for the targets
    :type Agent_graph: Networkx undirected graph
    :param num_agents: Number of agents for assignments
    :return:
    path_list: Lists of paths for each agent
    cost_obtained: Maximum cost of the paths
    """

    #Generate minimum spanning tree
    tree=generate_minimumspanning_tree(Agent_graph)
    #Prints the ordered edges in the tree
    #print(sorted(tree.edges(data=True)))


    #Compute approximate Eulerian tour
    tour_min=min_hamilton(tree)
    #Prints the edges of eulerian tour
    #print("Edges of the tour",tour_min)
    #Compute the overall cost
    cost_tour = compute_cost(Agent_graph, tour_min)
    print("Cost of the min_tour:", cost_tour)

    #Assign parts of the min cost eulerian tour to each agent by bisection
    path_list,cost_obtained=bisection_loop(Agent_graph,tour_min,num_agents)

    #Print list of paths, number of paths, max_cost
    print("paths for each agent",path_list)
    print("Number of total paths",len(path_list))

    print("Max cost of paths", 4*cost_obtained)
    return(path_list,cost_obtained)


def bisection_loop(Agent_graph,tour_min,num_agents):
    """
    :param Agent_graph: Networkx graph for the targets
    :type Agent_graph: Networkx undirected graph
    :param tour_min: List of nodes for the approximate minimum cost Eulerian tour
    :type tour_min: List of nodes
    :param num_agents: Number of agents for assignments
    :return:
    all_agentlist: List of paths for each agent
    cost_bisec: Maximum cost of the paths of the agents
    """

    #Bisection over optimal costcost
    cost_low=0
    cost_upper=10000
    while cost_upper-cost_low>1e-6:
        cost_bisec=(cost_upper+cost_low)/2

        #Initialze lists for agents
        cost_agent=0
        all_agentlist=[]
        agent_list=[]
        #Go over the eulerian tour
        for i in range(len(tour_min)-1):
            #Add the cost of the constructed tour, and add the edges to the list
            cost_agent=cost_agent+Agent_graph[tour_min[i]][tour_min[i+1]]['weight']
            agent_list.append((tour_min[i],tour_min[i+1]))

            # If the cost exceeds 4x of the optimal cost, break the tour of this agent
            if cost_agent>4*(cost_upper+cost_low)/2:
                all_agentlist.append(agent_list)
                agent_list=[]
                #print(cost_agent)
                cost_agent=0
        #If the number of tours is less or equal than the
        # number of agents, we increase our guess of the optimal cost
        if len(all_agentlist)>=num_agents:
            cost_low=(cost_upper+cost_low)/2
        #Else, we lower our guess of optimal cost
        else:
            cost_upper=(cost_upper+cost_low)/2

    #Returns the paths for each agent, and the optimal cost,
    # which is guaranteed to be a 4 approximation for planar graphs
    return (all_agentlist,cost_bisec)


#Computes an approximately optimal hamiltonian path from a minimum spanning tree
def min_hamilton(tree):
    """
    :param tree: List of edges in the minimum spanning tree
    :type: tree: Set of networkx edges
    :return:
    step_list: Ordered nodes of the Eulerian tour
    """

    step_list=[]
    # Go over the edges of tree, add to the Eulerian tour if they are not already present
    for item,item2,weight in sorted(tree.edges(data=True)):
        #print(item,item2,weight)
        if item not in step_list:
            step_list.append(item)

        if item2 not in step_list:
            step_list.append(item2)
    return(step_list)

def generate_Graph(m,T,env):
    """

    :param m: FiMDP model
    :param T: set of targets: which is a proxy here
    :param env: FiMDP env
    :return:
    Agent_graph: Networkx graph with nodes representing each target, edges representing cost
    """

    #Generate nodes of the agent
    Agent_graph= nx.Graph()
    count=0
    for item in T:
        count=count+1
        Agent_graph.add_node((item))

    #Generate edge costs for the agent
    for item in Agent_graph:
        for item2 in Agent_graph:
            if not item==item2 and not (item,item2) in Agent_graph.edges:
                Agent_graph.add_edge(item,item2,weight=np.random.uniform(0, 20))

    #return the networkx graph
    return Agent_graph

#Computes minimum spanning tree, used to generate minimum cost path
def generate_minimumspanning_tree(Agent_graph):
    """

    :param Agent_graph: Networkx graph for the targets
    :type Agent_graph: Networkx undirected graph
    :return:
    Tree: minimum spanning tree
    """
    Tree = nx.minimum_spanning_tree(Agent_graph)
    return Tree

#Compute the cost of the path
def compute_cost(Agent_graph,tour):
    """
    :param Agent_graph: Networkx graph for the targets
    :type Agent_graph: Networkx undirected graph
    :param tour: Nodes of the Eulerian tour
    :type tour: python list
    :return:
    cost: Cost of the Eulerian tour
    """
    cost=0
    for i in range(len(tour)-1):

        cost=cost+Agent_graph[tour[i]][tour[i+1]]['weight']
    return cost

