import math
import copy
import json

def graph_from_json(file_path):
    with open(file_path,'r') as f:
        graph_file = json.load(f)

    graph = CMDP()

    for node in graph_file["nodes"]:
        graph.addNode(node["label"],isAction=node["action"],isReload=node["reload"])

    for edge in graph_file["edges"]:
        graph.GetNode(edge["tail"]).insert(graph.GetNode(edge["head"]),consumed=edge["consumption"], probability=edge["probability"])

    graph.finalizeCMDP()

    return graph, graph_file["cmax"]

def get_T_from_json(file_path, graph):
    with open(file_path,'r') as f:
        graph_file = json.load(f)

    if not "T" in graph_file:
        raise KeyError('No T in ' + file_path)

    T = []
    for node in graph_file["T"]:
        T.append(graph.GetNode(node["label"]))

    return T


class CMDP:

    def __init__(self):
        self.nodes = set()
        self.numNodes = 0
        self.numbertrack = 0


    def addNode(self,label,isAction = False, isReload = False):
        check = True
        for node in self.nodes:
            if node.label == label:
                check = False
        if check:
            if isAction:
                node = CMDP.Node(label,None,self.numNodes,isAction,isReload)
                self.nodes.add(node)
                self.numNodes += 1
            else:
                node = CMDP.Node(label, self.numbertrack, self.numNodes, isAction, isReload)
                self.nodes.add(node)
                self.numNodes += 1
                self.numbertrack += 1
                self.numNodes += 1
        return node

    def removeNodes(self,NodeSet):
        removeset = set()
        for node in self.nodes:
            for v in NodeSet:
                if node.label == v.label:
                    removeset.add(node)
        for node in removeset:
            self.nodes.remove(node)
    def subtractCMDP(self,CMDP_):
        removeSet = set()
        if isinstance(CMDP_,CMDP):
            for node in CMDP_.nodes:
                for v in self.nodes:
                    if v.label == node.label:
                        removeSet.add(v)
            for node in removeSet:
                self.remove_node(node)

        elif isinstance(CMDP_,set):
            for node in CMDP_:
                for v in self.nodes:
                    if v.label == node.label:
                        removeSet.add(v)
            for node in removeSet:
                self.remove_node(node)
        else:
            AttributeError

    def remove_node(self, Node):
        self.nodes.remove(Node)
        for i in self.nodes:
            check = False
            for j in i.adj:
                if j[0] == Node:
                    check = j
                    break
            if check:
                i.adj.remove(j)
                # self.numNodes -= 1

    def addNewStates(self,name,iterator):
        for i in iterator:
            self.addNode(name + i.str())

    class Node:
        def __init__(self,label,number,NumNodes,isaction = False,isReload = False):
            self.adj = set()
            self.prv = set()
            self.number = number
            self.label = label
            self.action = isaction
            self.reload = isReload
            self.number = number
            self.Fv = 0
        def insert(self,Node,consumed = 0,probability = None):
            # self.adj.add(Node)
            if not probability == None:
                # self.probability.insert(Node.number,probability)
                self.adj.add((Node,consumed,probability))
            else:
                  self.adj.add((Node,consumed,1))
                # else:
                    # print('This node is not an action')
        def reloadSwitch(self,Reloadbool):
            self.reload = Reloadbool


    def finalizeCMDP(self):
        self.edges = []
        self.actions = []
        self.states = []
        for node in self.nodes:
            if node.action:
                self.actions.append(node)
            else:
                self.states.append(node)
            for adja in node.adj:
                self.edges.append((node,adja[0],adja[1],adja[2]))



    def isSafe(self,d,cap):
        Rtemp = set()
        tempMDCP = copy.copy(self)
        mininit = tempMDCP.minInitConsForSafe()
        for node in tempMDCP.states:
            if node.reload:
                Rtemp.add(node)
        RnotCap = set()
        while True:
            for s in Rtemp:
                if mininit[s.number] > cap:
                    RnotCap.add(s)
            if len(RnotCap) == 0:
                break
            for s in RnotCap:
                s.reload = False
                Rtemp.remove(s)
            RnotCap = set()
            mininit = tempMDCP.minInitConsForSafe()
        safeDict = [False]*len(self.states)
        for s in tempMDCP.states:
            if mininit[s.number] <= d:
                safeDict[s.number] = True
            else:
                safeDict[s.number] = False

        return safeDict












    def GetNode(self,label):
            for node in self.nodes:
                if node.label == label:
                    return node



    def addEdge(self,v,w,prob=None,consump=None):
        if not prob == None:
            cm.GetNode(v).insert(cm.GetNode(w), probability=prob)
        if not consump == None:
            cm.GetNode(v).insert(cm.GetNode(w), consumed=consump)

    def DFSUtil(self,v,visited,SCC):
        visited[v.number] = True


        for i in v.adj:
            if not visited[i[0].number]:
                self.DFSUtil(i[0],visited,SCC)
        SCC.add(v)



    def fillorder(self,v,visited,stack):
        visited[v.number] = True
        for i in v.adj:
            if not visited[i[0].number]:
                self.fillorder(i[0],visited,stack)
        stack.append(v)

    def getTranspose(self):
        g = CMDP()
        for v in self.nodes:
            g.addNode(v.label, isAction=v.action, isReload=v.reload)

        for v in self.nodes:
            for i in v.adj:
                # try:
                #     prob = i[2]
                # except IndexError:
                #     prob = None
                g.GetNode(i[0].label).insert(g.GetNode(v.label),consumed=i[1],probability=0)

        return g

    def getSCCs(self):
        #TODO:Improve with Tarjan Algorithm
        SCCs = []
        stack = []

        visited = [False]*self.numNodes

        for i in self.nodes:
            if not visited[i.number]:
                self.fillorder(i,visited,stack)

        gr = self.getTranspose()

        visited = [False]*self.numNodes

        while stack:
            i = stack.pop()
            if not visited[gr.GetNode(i.label).number]:
                SCC = set()
                gr.DFSUtil(gr.GetNode(i.label),visited,SCC)
                SCCs.append(SCC)
        realSCCs = []
        for i in SCCs:
            SCC = set()
            for v in i:
                SCC.add(self.GetNode(v.label))
            realSCCs.append(SCC)
        return realSCCs

        ##This likely does not work. Go to Faster and Dynamic Algorithms For Maximal End-Component Decomposition
        ##And Related Graph Problems In Probabilistic Verification for better algorithm

    def getBSCCs(self):
        BSCCs = []
        SCCs = self.getSCCs()
        for SCC in SCCs:
            check = True
            for v in SCC:
                for w in v.adj:
                    if not w[0] in SCC:
                        check = False
                        break
            if check:
                BSCCs.append(SCC)

        return BSCCs

    def neverEscape(self,X):
        X_ = CMDP()
        check = CMDP()
        for _ in range(len(self.nodes)):
            for node in X.nodes:
                if node.action:
                    flag = True
                    if node.label == 'redaction2':
                        print('debug')
                    for v in node.adj:
                        flag2 = False
                        for w in X.nodes:
                            if v[0].label == w.label:
                                flag2 = True
                                break
                        if not flag2:
                            flag = False
                    if flag:
                        X_.addNode(node.label)
                elif not node.action:
                    for v in node.adj:
                        for w in X.nodes:
                            if v[0].label == w.label:
                                X_.addNode(node.label)
                                break

            #X_ is a subset of X
            if len(X_.nodes) == len(check.nodes):
                break
            check = copy.deepcopy(X_)
        return X_



    def getMECs(self):
        list = []
        G = copy.deepcopy(self)
        while not len(G.nodes)==0:
            BSCCs = G.getBSCCs()
            R = set()
            G_ = copy.deepcopy(G)
            for B in BSCCs:
                list.append(B)
                #TODO: Make this more efficient
                VminB = copy.deepcopy(G)
                VminB.removeNodes(B)
                SafeX = G.neverEscape(VminB)
                VminSafeX = copy.deepcopy(G)
                # debugchk = VminSafeX.subtractCMDP(SafeX)
                VminSafeX.subtractCMDP(SafeX)
                R = R.union(VminSafeX.nodes)
                print(R)
            G.subtractCMDP(R)
        removelist = []
        for i, elem in enumerate(list):
            if len(elem) == 1:
                check = False
                for node in elem:
                    for v in node.adj:
                        if v[0].label == node.label:
                            check = True
                if not check:
                    removelist.append(i)
        for i in sorted(removelist,reverse=True):
            del list[i]
        return list





    def Attractor(self,U0):
        U = []
        U.insert(0,U0)
        for i in range(100):
            U.insert(i+1,set())
            Vp = set()
            V1 = set()
            for v in self.nodes:
                if v.action:
                    if not len(set(j[0] for j in v.adj).intersection(U[i])) == 0:
                        Vp.add(v)
                else:
                    if set(j[0] for j in v.adj).issubset(U[i]):
                        V1.add(v)
            U[i+1] = U[i].union(Vp.union(V1))
        return U[-1]

    def getZeroMECs(self):
        tempCMDP = copy.deepcopy(self)
        for v in tempCMDP.isNodeState(action=False):
            collection = set()
            for i in v.adj:
                if i[1] > 0:
                    collection.add(i)
            for i in collection:
                tempCMDP.remove_node(i[0])
        zeroMECs = tempCMDP.getMECs()


        return zeroMECs


    #TODO: Still unfinished
    def safeBuchi(self,sinit,d,cap,T):
        sinit = self.GetNode(sinit)
        Hlist = self.getZeroMECs()
        tempCMDP = copy.deepcopy(self)
        k = len(Hlist)
        tempCMDP.addNewStates('s',range(k))
        for i in range(k):
            check = True
            for node in T:
                for v in Hlist[i]:
                    if v.label == node.label:
                        check = False
            s = tempCMDP.GetNode('s' + i.str())
            if check:
                tempCMDP.addNode('acycle'+i.str())
                s.insert(tempCMDP.GetNode('acycle' + i.str()))
                tempCMDP.GetNode('acycle' + i.str()).insert(s,probability=1)
                s.reloadSwitch(True)
            else:
                reloadCheck = False
                for node in Hlist[i]:
                    if not node.action:
                        for action in node.adj:
                            check = False
                            for v in Hlist[i]:
                                if v.action:
                                    if action.label == v.label:
                                        check = True
                            if not check:
                                s.insert(action.label)
                        s.insert(tempCMDP.GetNode(action.label))
                    if node.reload:
                        reloadCheck = True
                if not reloadCheck:
                    s.reloadSwitch(True)
                ##Replace every occurence of every state of ...



    def bounding(self,x,y):
        if x <= y:
            return x
        else:
            return math.inf

    def rOperator(self,T):
        r = [math.inf]*len(self.states)
        for s in self.states:
            if not hasattr(T, 'adj'):
                for i in T:
                    if s.label == i.label:
                        r[s.number] = 0
                    else:
                        r[s.number] = math.inf
            else:
                if s.label == T.label:
                    r[s.number] = 0
                else:
                    r[s.number] = math.inf

        return r



    def maxSafeSucc(self,a,cap,cmax, safe_cap):
        if len(a.adj) > 1:
            # temp = max(a.adj,key=(lambda x:self.safeMinimizer(cap,cmax,x[0])))
            templist = [x for x in a.adj]
            tempmax = 0
            for vert in templist:
                temp = safe_cap[vert[0].number]
                if temp > tempmax:
                    tempmax = temp
        else:
            for temp in a.adj:
                return safe_cap[temp[0].number]

        return tempmax


    def safeMinimizer(self,cap):
        #Find minimum d that satisfies self.isSafe(i,cap,self.GetNode(s.label)) given cap
        # tempmin = dmax
        # curr_d = math.ceil(dmax/2)
        # frac = math.ceil(curr_d/2)
        # check = False

        safe_minimums = [math.inf]*len(self.states)

        for curr_d in range(cap):
            print('Safe Minimize Progress: {} out of {}'.format(curr_d,cap))
            safeCheck = self.isSafe(curr_d, cap)
            for node in self.states:
                if safeCheck[node.number]:
                    safe_minimums[node.number] = curr_d

        return safe_minimums

        # if not self.isSafe(dmax,cap)[s]:
        #     print('{} is at max'.format(s.label))
        #     return dmax
        # for _ in range(dmax):
        #     print(curr_d)
        #     if not curr_d < 0:
        #         safeCheck = self.isSafe(curr_d, cap)
        #         if safeCheck[s]:
        #             tempmin = min(tempmin,curr_d)
        #             curr_d -= frac
        #         else:
        #             curr_d += frac
        #     else:
        #         curr_d += frac
        #     if frac == 1:
        #         check = True
        #     frac = math.ceil(frac/2)
        #     if check:
        #         safeCheck = self.isSafe(curr_d, cap)
        #         if safeCheck[s]:
        #             tempmin = min(tempmin,curr_d)
        #         return tempmin

    def safePosReachDebug(self,cap,T,cmax):
        ##Is there a strategy that starts at sinit and hits states T and is safe(d,cap)?


        safe_cap = self.safeMinimizer(cap)

        bell = self.calculate_Bellman(T, cap, cmax, safe_cap)

        # for i, entry in enumerate(bell):
        #     if entry <=d:
        #         bell[i] = True
        #     else:
        #         bell[i] = False
        return bell

    def calculate_Bellman(self,T, cap, cmax, safe_cap):
        r = self.rOperator(T)
        for iter in range(2 * len(self.states)):
            # print('{} out of {}'.format(iter, 2 * len(self.states)))
            r, check = self.Bellman(r, cap, cmax, T, safe_cap)
            if check:
                break
        return r



    def Bellman(self,r, cap, cmax, T, safe_cap):
        r_copy = copy.copy(r)
        check = False
        check_sum = 0
        for state in self.states:
            tempmin = math.inf
            for act in state.adj:
                max_safe = self.maxSafeSucc(act[0], cap, cmax, safe_cap)
                min_r = min([r[state[0].number] for state in act[0].adj])
                max_1 = max(max_safe,min_r)
                tempmin = min(tempmin, act[1] + max_1)
            if not self.GetNode(state.label) in T:
                r_copy[state.number] = self.bounding(tempmin, cap)
            if not r_copy[state.number] == r[state.number]:
                check = True
            else:
                check_sum += 1
        print('{} out of {} converged'.format(check_sum,len(self.states)))
        return r_copy, check

    def minInitConsForSafe(self):
        self.mininit = [math.inf]*len(self.states)
        m = len(self.states)
        for _ in range(m):
            for node in self.states:
                tempmin = math.inf
                for a in node.adj:
                    max_1 = 0
                    for i in a[0].adj:
                        if i[0].reload:
                            max_1 = max(max_1, 0)
                        else:
                            max_1 = max(max_1, self.mininit[i[0].number])

                    tempmin = min(tempmin, a[1] + max_1)
                self.mininit[node.number] = tempmin
        return self.mininit

    def minInitConsDebug(self):
        self.mininit = {}
        m = len(self.states)
        for node in self.states:
            self.mininit[node] = node.Fv
        for _ in range(m):
            for node in self.states:
                if node.reload:
                    self.mininit[node] = 0
                else:
                    tempmin = math.inf
                    for a in node.adj:
                        tempmin = min(tempmin, a[1] + max([self.mininit[i[0]] for i in a[0].adj]))
                    self.mininit[node] = tempmin
        return self.mininit








if __name__ == "__main__":

    cm = CMDP()
    cm.addNode('blue',isReload=True)
    cm.addNode('blueaction1',isAction=True)
    cm.addNode('red',isReload=False)

    #Make a MEC for testing
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

    # cm.addEdge('green','greenaction2',consump=2)
    # cm.addEdge('greenaction2','cyan',prob=1)
    # cm.addEdge('cyanaction1','green',prob=1)
    # cm.addEdge('cyan','cyanaction1',consump=15)
    # cm.MinInitCons(cm.GetNode('cyan'),printCheck=True)
    # cm.MaxRcap(15,printCheck=True)
    # cm.isSafe(4,17,'blue',printCheck=False)
    # scc = cm.getSCCs()
    # print(scc)

    # BSCCs = cm.getBSCCs()
    # print(BSCCs)
    #
    # MECs = cm.getMECs()
    # print(MECs)
    #
    # zMECs = cm.getZeroMECs()
    # print
    # print(cm.isSafe(5,5,cm.GetNode('zero'),printCheck=True))

    cm.MinInitCons(cm.GetNode('blue'))
    cm.minInitConsDebug()
    print('')