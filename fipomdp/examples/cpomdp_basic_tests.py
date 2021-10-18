from fimdp import ConsMDP


def basic():
    m = ConsMDP(layout="neato")

    m.new_states(9)
    for s in [0, 7]:
        m.set_reload(s)

    m.add_action(0, {1: 1}, "", 1)
    m.add_action(1, {0: 1}, "", 1)
    m.add_action(2, {1: 1}, "", 1)
    m.add_action(3, {2: .5, 1: .5}, "", 1)
    m.add_action(3, {4: .5, 6: .5}, "t", 10)
    m.add_action(4, {5: 1}, "t", 1)
    m.add_action(5, {6: 1}, "r", 1)
    m.add_action(6, {3: .5, 7: .5}, "t", 6)
    m.add_action(6, {7: 1}, "r", 1)
    m.add_action(7, {3: 1}, "", 20)
    m.add_action(7, {6: 1}, "t", 3)
    m.add_action(8, {7: .5, 2: .5}, "", 5)

    targets = set([2, 5])

    return m, targets