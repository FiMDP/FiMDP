from fimdp.io import prism_to_consmdp, parse_cap_from_prism, \
    consmdp_to_storm_consmdp, storm_sparsemdp_to_consmdp, \
    encode_to_stormpy
from fimdp.energy_solvers import BasicES
from fimdp.objectives import BUCHI, AS_REACH
from fimdp.examples.reachability_examples import little_alsure
from fimdp.explicit import product_energy
import stormpy

mdp = prism_to_consmdp("prism_models/gw_50_full.prism")
assert mdp.num_states == 2500, ("Wrong number of states: "
                                f"{mdp.num_states} instead of 2500.")
solver = BasicES(mdp, cap=180, targets=[620])
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
                              f"{mdp.num_states} instead of 25.")
solver = BasicES(mdp, cap=10, targets=[21])
expected = [8, 7, 6, 7, 6, 3, 0, 6, 3, 7, 6, 3, 6, 6, 3, 7, 8, 7, 6, 7, 8, 6, 7, 8, 7]
result = solver.get_min_levels(BUCHI)
assert result == expected, "Wrong minimal levels."

print("Passed test 4 for prism_to_consmdp.")

cap = parse_cap_from_prism("prism_models/gw_5_full.prism")
assert cap == 10

print("Passed test 1 for parse_cap_from_prism")

mdp, targets = prism_to_consmdp("prism_models/gw_5_full.prism",
                                return_targets=True)
solver = BasicES(mdp, cap, targets)
result = solver.get_min_levels(BUCHI)
assert result == expected, "Wrong minimal levels."

print("Passed test 5 for prism_to_consmdp (targets)")

# ConsMDP to Storm
m, T = little_alsure()
storm = consmdp_to_storm_consmdp(m)
result = storm.to_dot()
expected = """digraph model {
	0 [ label = "0: {}" ];
	1 [ label = "1: {}" ];
	2 [ label = "2: {}" ];
	3 [ label = "3: {reload}" ];
	"0c0" [shape = "point"];
	0 -> "0c0" [ label = "{t}"]
;
	"0c0" -> 1 [ label= "0.5" ];
	"0c0" -> 2 [ label= "0.5" ];
	"0c1" [shape = "point"];
	0 -> "0c1" [ label = "{pos}"]
;
	"0c1" -> 1 [ label= "0.5" ];
	"0c1" -> 3 [ label= "0.5" ];
	"1c0" [shape = "point"];
	1 -> "1c0" [ label = "{r}"]
;
	"1c0" -> 3 [ label= "1" ];
	"2c0" [shape = "point"];
	2 -> "2c0" [ label = "{r}"]
;
	"2c0" -> 3 [ label= "1" ];
	"3c0" [shape = "point"];
	3 -> "3c0" [ label = "{r}"]
;
	"3c0" -> 3 [ label= "1" ];
}
"""
assert result == expected, "The output for storm does not match the expected one"

print("Passed test 1 for consmdp_to_storm_consmdp")

storm = consmdp_to_storm_consmdp(m, T)
result = storm.to_dot()
expected = """digraph model {
	0 [ label = "0: {}" ];
	1 [ label = "1: {target}" ];
	2 [ label = "2: {target}" ];
	3 [ label = "3: {reload}" ];
	"0c0" [shape = "point"];
	0 -> "0c0" [ label = "{t}"]
;
	"0c0" -> 1 [ label= "0.5" ];
	"0c0" -> 2 [ label= "0.5" ];
	"0c1" [shape = "point"];
	0 -> "0c1" [ label = "{pos}"]
;
	"0c1" -> 1 [ label= "0.5" ];
	"0c1" -> 3 [ label= "0.5" ];
	"1c0" [shape = "point"];
	1 -> "1c0" [ label = "{r}"]
;
	"1c0" -> 3 [ label= "1" ];
	"2c0" [shape = "point"];
	2 -> "2c0" [ label = "{r}"]
;
	"2c0" -> 3 [ label= "1" ];
	"3c0" [shape = "point"];
	3 -> "3c0" [ label = "{r}"]
;
	"3c0" -> 3 [ label= "1" ];
}
"""
assert result == expected, "The output for storm does not match the expected one"

print("Passed test 2 for consmdp_to_storm_consmdp")

assert m.get_dot() == storm_sparsemdp_to_consmdp(storm).get_dot()
print("Passed test for consmdp_to_storm_consmdp and storm_sparsemdp_to_consmdp")

constants = {
    "size_x" : 10,
    "size_y" : "size_x",
    "capacity" : 18,
    "cons_w_ex" : 0,
    "cons_s_ex" : 0,
}
mdp = prism_to_consmdp("prism_models/gw_param.prism", constants=constants)
expected = pow(constants["size_x"], 2)
result = mdp.num_states
assert result == expected, "The output parametric model has a wrong number of" \
                           f"states. Is {result}, expected {expected}"

print("Passed test 1 for parametric models")

constants = {
    "size_x" : 100,
    "size_y" : "size_x",
    "capacity" : 250,
    "cons_w_ex" : 0,
    "cons_s_ex" : 0,
}
mdp = prism_to_consmdp("prism_models/gw_param.prism", constants=constants)
expected = pow(constants["size_x"], 2)
result = mdp.num_states
assert result == expected, "The output parametric model has a wrong number of" \
                           f"states. Is {result}, expected {expected}"

print("Passed test 2 for parametric models")

constants = {
    "size_x" : 15,
    "size_y" : "size_x",
    "capacity" : 35,
    "cons_w_ex" : 1,
    "cons_s_ex" : 3,
}
mdp = prism_to_consmdp("prism_models/gw_param.prism", constants=constants)

print("Passed test 3 for parametric models")

constants = {
    "size_x" : 10,
    "size_y" : "size_x",
    "capacity" : 18,
    "cons_w_ex" : 0,
    "cons_s_ex" : 0,
}
mdp, targets = prism_to_consmdp("prism_models/gw_param.prism",
                                constants=constants,
                                return_targets=True)
capacity = constants["capacity"]
storm_mdp = encode_to_stormpy(mdp, capacity, targets)

# Get the FiMDP result
solver = BasicES(mdp, capacity, targets)
fimdp_res = solver.get_min_levels(AS_REACH)

# Get the Storm result
formula = 'Pmax>=1 [F "target" & Pmax>=1 [F "reload"]]'
prop = stormpy.parse_properties(formula)
storm_result = stormpy.model_checking(storm_mdp, prop[0])

# Check equivalence of results
product, _ = product_energy(mdp, capacity)
for s in range(product.num_states):
    state, energy = product.components[s]
    if energy == "-∞":
        assert not storm_result.at(s)
        continue
    assert storm_result.at(s) == (int(energy) >= fimdp_res[state])

print("Passed test 1 for encode_to_stormpy")
