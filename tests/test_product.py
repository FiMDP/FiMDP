# -*- coding: utf-8 -*-
# +
import spot
spot.setup()
from spot.jupyter import display_inline

from math import inf

from fimdp.labeledConsMDP import LCMDP
from fimdp.energy_solver import BUCHI
from fimdp.products import DBAWrapper
# -

# ### Test DBAWrapper

f = spot.formula("GF b & GF a")
aut = spot.translate(f, "BA", "deterministic", "complete")

aut

# +
AP = ["a","b"]
wrapper = DBAWrapper(aut, AP)

a = AP.index("a")
b = AP.index("b")
assert wrapper.succ(2, [a]) == 1
assert wrapper.succ(2, [a, b]) == 2
assert wrapper.succ(2, [b]) == 0
assert wrapper.succ(2, []) == 1

assert wrapper.succ(0, [b]) == 0
assert wrapper.succ(1, [a, b]) == 2

print("Passed test for DBAWrapper in file test_product.py")
# -

# ## Test product

# In the following example we want the states `1` and `2` to be visited infinitely often, expressed naturaly as the formula $\mathsf{G}\mathsf{F} s_1 \land \mathsf{G}\mathsf{F}s_2$ where the atomic proposition $s_1$ corresponds to visiting state `1` and the tomic proposition $s_2$ corresponds to visiting state`2`.

from fimdp.examples.reachability_examples import product_example
mdp, T = product_example()
mdp

# We create labeled consumption MDP with corresponding atomic propositions and label the states accprdngly using indices into the `AP` list.

lmdp = LCMDP(AP=["s1","s2"], mdp=mdp)
lmdp.state_labels = [set(), {0}, {1}, set()]

# Create a deterministic automaton for the desired formula

f = spot.formula("GF s1 & GF s2")
aut = spot.translate(f, "BA", "deterministic", "complete")
assert aut.is_deterministic()
aut

# Build the product. It should contain states named in the form `mdp_state,automaton_state`.

p, T = lmdp.product(aut)
assert p.names == ['0,1', '1,0', '2,1', '3,1', '3,0', '0,0', '2,2']
print("Passed test 1 for product in file test_product.py")

res = p.get_Buchi(T, 5, True)
assert res == [inf, inf, inf, inf, inf, inf, inf]
print("Passed test 2 for product in file test_product.py")

# +
res = p.get_Buchi(T, 9, True)
res = p.energy_levels.get_strategy(BUCHI)

result = []
for rule in res:
    result.append({k: v.label for k, v in rule.items()})
assert result == [{6: 'α', 2: 'β'}, {3: 'r'}, {1: 'r'}, {0: 's'}, {0: 's'}, {2: 'β'}, {1: 'r'}]
print("Passed test 3 for product in file test_product.py")
# -

# ### Test ProductSelectorWrapper

from fimdp.products import ProductSelectorWrapper

orig, aut = 3, 0
p_s = p.components_to_states_d[(orig, aut)]
expected = res.select_action(p_s, 4)
expected

p_selector = ProductSelectorWrapper(p, res)
result = p_selector.select_action(orig, aut, 4)
result

assert expected.label == result.label
assert expected.cons == result.cons
prod_dest = list(expected.distr.keys())[0]
orig_dest, _ = p.components[prod_dest]
assert orig_dest in result.distr
assert expected.distr[prod_dest] == result.distr[orig_dest]
print("Passed test for ProductSelectorWrapper in file test_product.py")
