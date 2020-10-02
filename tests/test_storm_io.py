from fimdp.io import prism_to_consmdp
from fimdp.energy_solvers import BasicES
from fimdp.objectives import BUCHI

mdp = prism_to_consmdp("prism_models/gw_50_full.prism")
assert mdp.num_states == 2500, ("Wrong number of states: "
                                f"{mdp.num_states} instead of 2500.")
solver = BasicES(mdp, cap=80, targets=[620])
solver.get_min_levels(BUCHI)

expected = "0: x=0 y=0"
result = mdp.names[0]
assert result == expected, ("Wrong state name, should be: "
                            f"`{expected}` and is `{result}`.")
print("Passed test 1 for prism_to_consmdp.")

try:
    prism_to_consmdp("prism_models/gw_50_norew.prism")
    assert False, "Detection of missing consumption failed"
except ValueError as e:
    print("Passed test 2 for prism_to_consmdp. [no consumption]")

try:
    prism_to_consmdp("prism_models/gw_50_norel.prism")
    assert False, "Detection of missing reloads failed"
except ValueError as e:
    print("Passed test 3 for prism_to_consmdp. [no reloads]")


mdp = prism_to_consmdp("prism_models/gw_5_full.prism")
assert mdp.num_states == 25, ("Wrong number of states: "
                              f"{mdp.num_states} instead of 2500.")
solver = BasicES(mdp, cap=10, targets=[18])
expected = [8, 7, 6, 7, 6, 3, 0, 6, 3, 7, 6, 3, 6, 6, 3, 7, 8, 7, 6, 7, 8, 6, 7, 8, 7]
result = solver.get_min_levels(BUCHI)
assert result == expected, "Wrong minimal levels."

print("Passed test 4 for prism_to_consmdp.")