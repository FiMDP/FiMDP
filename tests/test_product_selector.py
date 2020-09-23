# -*- coding: utf-8 -*-
# +
import spot
spot.setup()
from spot.jupyter import display_inline

from fimdp.core import ProductSelector
from fimdp.energy_solver import BasicES, BUCHI
from fimdp.labeledConsMDP import LCMDP

# -

from fimdp.examples.reachability_examples import product_example
mdp, T = product_example()
lmdp = LCMDP(AP=["s1","s2"], mdp=mdp)
lmdp.state_labels = [set(), {0}, {1}, set()]
lmdp

# Create a deterministic automaton for the desired formula

f = spot.formula("GF s1 & GF s2")
aut = spot.translate(f, "BA", "deterministic", "complete")
assert aut.is_deterministic()

# Create product.

product, _ = lmdp.product_with_dba(aut)

# Create ProductSelector and fill a few rules manualy using the product states and actions.

# +
selector = ProductSelector(product)

def ith_action_for(s, i=1):
    k = 1
    it = product.actions_for_state(s)
    while k < i:
        it.__next__()
        k += 1
    return it.__next__()


# -

# This should go well
selector.update(5, 10, ith_action_for(5))
selector.update(5, 6, ith_action_for(5, 2))
assert selector.select_action(0, 0, 12).label == "α"
assert selector.select_action(0, 0, 9).label == "β"
print("Passed test 1 for ProductSelector")

# Check action belonging to a different state
try:
    selector.update(5, 10, ith_action_for(4))
    assert False
except ValueError:
    print("Passed test 2 for ProductSelector")

# Check KeyError for non-existing combination
try:
    selector.select_action(0, 1, 12)
    assert False
except KeyError:
    print("Passed test 3 for ProductSelector")   

action = selector.select_action(0, 0, 12)
assert action in lmdp.actions_for_state(0)
print("Passed test 4 for ProductSelector") 

# ## Equivalence of ProductSelectorWrapper to ProductSelector

from fimdp.core import ProductSelectorWrapper

# Create ProductSelector and initialize it using CounterSelector for product

psolver = BasicES(product, 9, T)
p_selector = psolver.get_strategy(BUCHI)
selector = ProductSelector(product)
for state, rule in enumerate(p_selector):
    for energy, action in rule.items():
        selector.update(state, energy, action)

wrapper = ProductSelectorWrapper(product, p_selector)

for p_s in range(product.num_states):
    orig, other = product.components[p_s]
    for energy in wrapper[p_s]:
        w_a = wrapper.select_action(orig, other, energy)
        s_a = selector.select_action(orig, other, energy)
        assert s_a == w_a
print("Passed test 5 for ProductSelector")

# ### Test behavior after deletion of the product

del product
del wrapper.mdp
del selector.product_mdp

try:
    wrapper.select_action(0,0,10)
    assert False
except AttributeError:
    pass

assert selector.select_action(0,0,10).label == "α"
print("Passed test 6 for ProductSelector") 
