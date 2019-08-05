from tools import CMDPgraph, GridWorld

#Generate a gridworld (Still need branching edges)
cmax_ = 3
graph = GridWorld.generate_GridWorld((10,10), cmax_,0.5)


#Example 2-state graph
g, cmax = CMDPgraph.graph_from_json('example.json')


T = CMDPgraph.get_T_from_json('example.json', g)

d = 5
cap = 6
bell = g.safePosReachDebug(d, cap, T, cmax)
print(bell[T[0]])



cm = CMDPgraph.CMDP()




##Example Graph:
###Improve with json file?
cm.addNode('blue',isReload=True)
cm.addNode('blueaction1',isAction=True)
cm.addNode('red',isReload=False)

#Make an MEC for testing
cm.addNode('redaction2',isAction=True)
cm.GetNode('red').insert(cm.GetNode('redaction2'),consumed=1)
cm.addNode('zero',isReload=True)
cm.GetNode('redaction2').insert(cm.GetNode('zero'),probability=1)
cm.addNode('zeroaction1',isAction=True)
cm.GetNode('zero').insert(cm.GetNode('zeroaction1'),consumed=3)
cm.addNode('one')
cm.GetNode('zeroaction1').insert(cm.GetNode('one'),probability=1)
cm.addNode('oneaction1',isAction=True)
cm.GetNode('one').insert(cm.GetNode('oneaction1'),consumed=2)
cm.GetNode('oneaction1').insert(cm.GetNode('zero'),probability=1)

cm.addNode('green',isReload=False)
cm.addNode('redaction1',isAction=True)
cm.addNode('greenaction1',isAction=True)
cm.GetNode('blue').insert(cm.GetNode('blueaction1'),consumed=2)
cm.GetNode('red').insert(cm.GetNode('redaction1'),consumed=1)
cm.GetNode('green').insert(cm.GetNode('greenaction1'),consumed=3)
cm.GetNode('blueaction1').insert(cm.GetNode('green'),probability=0.5)
cm.GetNode('blueaction1').insert(cm.GetNode('red'),probability=0.5)
cm.GetNode('redaction1').insert(cm.GetNode('green'),probability=0.5)
cm.GetNode('redaction1').insert(cm.GetNode('blue'),probability=0.5)
cm.GetNode('greenaction1').insert(cm.GetNode('blue'),probability=0.5)
cm.GetNode('greenaction1').insert(cm.GetNode('red'),probability=0.5)
cm.addNode('cyan',isReload=True)
cm.addNode('cyanaction1',isAction=True)
cm.addNode('greenaction2',isAction=True)

cm.GetNode('green').insert(cm.GetNode('greenaction2'),consumed=0)
cm.GetNode('greenaction2').insert(cm.GetNode('cyan'),probability=1)
cm.GetNode('cyanaction1').insert(cm.GetNode('green'),probability=1)
cm.GetNode('cyan').insert(cm.GetNode('cyanaction1'),consumed=1)



cm.finalizeCMDP()

check3 = cm.safePosReachDebug(20, 20, [cm.GetNode('one')], 3)

print(check3[cm.GetNode('red')])
