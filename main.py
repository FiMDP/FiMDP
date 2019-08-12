from tools import CMDPgraph, GridWorld
import math
import csv
import datetime

#Generate a gridworld (Still need branching edges)
cmax_ = 3
graph, cmax = CMDPgraph.graph_from_json('example.json')

T = CMDPgraph.get_T_from_json('example.json',graph)
print('Number of nodes: {}'.format(graph.numNodes))

bell = graph.safePosReachDebug( 20, T, cmax_)

print(graph.GetNode('node1').number)

check_node = '(2,2)'

print(bell)
print(datetime.datetime.today())

#Example 2-state graph
file_path = 'NYCstreetnetwork.json'

g, cmax = CMDPgraph.graph_from_json(file_path)

cmax = math.ceil(cmax)

T = CMDPgraph.get_T_from_json(file_path, g)

d = 15
cap = 25
bell = g.safePosReachDebug(cap, T, cmax)

w = csv.writer(open("output{}.csv".format(datetime.datetime.today()), "w"))
for state in g.states:
    w.writerow([state.label, bell[state.number]])




