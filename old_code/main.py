from tools import CMDPgraph, GridWorld
import math
import csv
import datetime

q#Example 2-state graph
file_path = 'NYCstreetnetwork.json'

g, cmax = CMDPgraph.graph_from_json(file_path)

cmax = math.ceil(cmax)

T = CMDPgraph.get_T_from_json(file_path, g)

cap = 50
bell = g.safePosReachDebug(cap, T, cmax)

#w = csv.writer(open("output{}.csv".format(datetime.datetime.today()), "w"))
#for state in g.states:
#    w.writerow([state.label, bell[state.number]])




