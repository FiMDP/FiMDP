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

                n_act1 = graph.addNode("(" + str(i) + "," + str(j) + ")_north1")
                n_act2 = graph.addNode("(" + str(i) + "," + str(j) + ")_north2")


                consumed = random.randrange(cmax)
                node.insert(n_act,consumed=consumed)
                states[i][j].insert(1, (n_act, 1))

                p = random.random()

                n_act.insert(n_act1,probability=p)
                n_act.insert(n_act2,probability=(1-p))

            if i < x_size - 1:
                e_act = graph.addNode("(" + str(i) + "," + str(j) + ")_east",isAction=True)

                e_act1 = graph.addNode("(" + str(i) + "," + str(j) + ")_east1")
                e_act2 = graph.addNode("(" + str(i) + "," + str(j) + ")_east2")

                consumed = random.randrange(cmax)
                node.insert(e_act, consumed=consumed)
                states[i][j].insert(2, (e_act,2))

                p = random.random()

                e_act.insert(e_act1, probability=p)
                e_act.insert(e_act2, probability=(1 - p))

            if not j == 0:
                s_act = graph.addNode("(" + str(i) + "," + str(j) + ")_south", isAction=True)

                s_act1 = graph.addNode("(" + str(i) + "," + str(j) + ")_south1")
                s_act2 = graph.addNode("(" + str(i) + "," + str(j) + ")_south2")

                consumed = random.randrange(cmax)
                node.insert(s_act, consumed=consumed)
                states[i][j].insert(3, (s_act, 3))

                p = random.random()

                s_act.insert(s_act1, probability=p)
                s_act.insert(s_act2, probability=(1 - p))
            if not i == 0:
                w_act = graph.addNode("(" + str(i) + "," + str(j) + ")_west", isAction=True)

                w_act1 = graph.addNode("(" + str(i) + "," + str(j) + ")_west1")
                w_act2 = graph.addNode("(" + str(i) + "," + str(j) + ")_west2")

                consumed = random.randrange(cmax)
                node.insert(w_act, consumed=consumed)
                states[i][j].insert(4, (w_act, 4))

                p = random.random()

                w_act.insert(w_act1, probability=p)
                w_act.insert(w_act2, probability=(1 - p))

    for i in range(x_size):
        for j in range(y_size):
            nodes = states[i][j][:]
            for _ in range(4):
                act = nodes.pop(-1)
                if hasattr(act, 'label'):
                    break
                elif act[1] == 4:
                    for index, nxt_state in enumerate(act[0].adj):
                        inter_act = graph.addNode(nxt_state[0].label + '-{}'.format(index),isAction=True)
                        inter_act.insert(states[i-1][j][0],probability=1)
                        nxt_state[0].insert(inter_act)
                elif act[1] == 3:
                    for index, nxt_state in enumerate(act[0].adj):
                        inter_act = graph.addNode(nxt_state[0].label + '-{}'.format(index), isAction=True)
                        inter_act.insert(states[i][j-1][0], probability=1)
                        nxt_state[0].insert(inter_act)
                elif act[1] == 2:
                    for index, nxt_state in enumerate(act[0].adj):
                        inter_act = graph.addNode(nxt_state[0].label + '-{}'.format(index), isAction=True)
                        inter_act.insert(states[i + 1][j][0], probability=1)
                        nxt_state[0].insert(inter_act)
                elif act[1] == 1:
                    for index, nxt_state in enumerate(act[0].adj):
                        inter_act = graph.addNode(nxt_state[0].label + '-{}'.format(index), isAction=True)
                        inter_act.insert(states[i][j + 1][0], probability=1)
                        nxt_state[0].insert(inter_act)
                else:
                    raise KeyError
    graph.finalizeCMDP()
    return graph