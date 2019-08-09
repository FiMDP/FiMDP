from tools import CMDPgraph, GridWorld
import math
import csv
import datetime

# #Generate a gridworld (Still need branching edges)
# cmax_ = 3
# graph = GridWorld.generate_GridWorld((3,3), cmax_,0.5)
#
# print('Number of nodes: {}'.format(graph.numNodes))
#
# bell = graph.safePosReachDebug(5, 5, [graph.GetNode('(0,0)')], cmax_)
#
# check_node = '(2,2)'
#
# if bell[graph.GetNode(check_node)]:
#     print(check_node + ' works')
# else:
#     print(check_node + ' does not work')
print(datetime.datetime.today())

#Example 2-state graph
file_path = 'NYCstreetnetwork.json'

g, cmax = CMDPgraph.graph_from_json(file_path)

cmax = math.ceil(cmax)

T = CMDPgraph.get_T_from_json(file_path, g)

d = 15
cap = 25
bell = g.safePosReachDebug(d, cap, T, cmax)

w = csv.writer(open("output{}.csv".format(datetime.datetime.today()), "w"))
for state in g.states:
    w.writerow([state.label, bell[state.number]])




