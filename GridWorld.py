from tools import CMDPgraph
import random


def generate_GridWorld(grid_size,cmax,reload_frac):
    graph = CMDPgraph.CMDP()
    states = []
    x_size = grid_size[0]
    y_size = grid_size[1]
    for i in range(x_size):
        states.insert(i,[])
        for j in range(y_size):
            states[i].insert(j,[])
            reload_bool = random.random() < reload_frac
            node = graph.addNode("(" + str(i) + "," + str(j) + ")",isReload=reload_bool)
            states[i][j].insert(0,node)
            if j < y_size - 1:
                n_act = graph.addNode("(" + str(i) + "," + str(j) + ")_north",isAction=True)
                consumed = random.randrange(cmax)
                node.insert(n_act,consumed=consumed)
                states[i][j].insert(1, (n_act, 1))
            if i < x_size - 1:
                e_act = graph.addNode("(" + str(i) + "," + str(j) + ")_east",isAction=True)
                consumed = random.randrange(cmax)
                node.insert(e_act, consumed=consumed)
                states[i][j].insert(2, (e_act,2))
            if not j == 0:
                s_act = graph.addNode("(" + str(i) + "," + str(j) + ")_south",isAction=True)
                consumed = random.randrange(cmax)
                node.insert(s_act, consumed=consumed)
                states[i][j].insert(3, (s_act, 3))
            if not i == 0:
                w_act = graph.addNode("(" + str(i) + "," + str(j) + ")_west",isAction=True)
                consumed = random.randrange(cmax)
                node.insert(w_act, consumed=consumed)
                states[i][j].insert(4, (w_act, 4))

    for i in range(x_size):
        for j in range(y_size):
            nodes = states[i][j][:]
            for _ in range(4):
                act = nodes.pop(-1)
                if hasattr(act, 'label'):
                    break
                elif act[1] == 4:
                    prob = random.random()
                    act[0].insert(states[i-1][j][0],probability=prob)
                    act[0].insert(states[i-1][j][0],probability=1-prob)
                    continue
                elif act[1] == 3:
                    prob = random.random()
                    act[0].insert(states[i][j-1][0],probability=prob)
                    act[0].insert(states[i][j-1][0],probability=1-prob)
                    continue
                elif act[1] == 2:
                    prob = random.random()
                    act[0].insert(states[i+1][j][0],probability=prob)
                    act[0].insert(states[i+1][j][0],probability=1-prob)
                    continue
                elif act[1] == 1:
                    prob = random.random()
                    act[0].insert(states[i][j+1][0],probability=prob)
                    act[0].insert(states[i][j+1][0],probability=1-prob)
                    continue
                else:
                    raise KeyError
    graph.finalizeCMDP()
    return graph