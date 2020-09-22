# -*- coding: utf-8 -*-
# +
import spot
spot.setup()
from spot.jupyter import display_inline

from math import inf

from fimdp.labeledConsMDP import LCMDP
from fimdp.energy_solver import BasicES, BUCHI
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

p, T = lmdp.product_with_dba(aut)
assert p.names == ['0,1', '1,0', '2,1', '3,1', '3,0', '0,0', '2,2']
print("Passed test 1 for product in file test_product.py")

psolver = BasicES(p, 5, T)
res = psolver.get_Buchi()
assert res == [inf, inf, inf, inf, inf, inf, inf]
print("Passed test 2 for product in file test_product.py")

# +
psolver.cap = 9
res = psolver.get_strategy(BUCHI, recompute=True)

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

# ### Test ProductSelector

from fimdp.products import ProductSelector
from fimdp.strategy import NoFeasibleActionError


def get_from_CounterSelector(counter_selector):
    res = ProductSelector(counter_selector.mdp)
    for s, rule in enumerate(counter_selector):
        for energy, action in rule.items():
            res.update(s, energy, action)
    return res


p_s = get_from_CounterSelector(res)

for s in range(p.num_states):
    orig_s, other_s = p.components[s]
    bounds = list(p_s[orig_s][other_s].keys())
    for energy in bounds:
        PS_orig_action = p_s.select_action(orig_s, other_s, energy)
        p_action = res.select_action(s, energy)
        assert PS_orig_action == p_selector.select_action(orig_s, other_s, energy)
        assert PS_orig_action == p.orig_action(p_action)
print("Passed test 1 for ProductSelector in file test_product.py")

# #### Test copy of Product selector

ps_copy = ProductSelector(p)
ps_copy.copy_values_from(p_s)
assert ps_copy == p_s
print("Passed test 2 for ProductSelector in file test_product.py")

# Partial copy

ps_copy = ProductSelector(p)
ps_copy.copy_values_from(p_s, [0,2,4,6])

# +
for s in [0,2,4,6]:
    orig_s, other_s = p.components[s]
    bounds = list(p_s[orig_s][other_s].keys())
    for energy in bounds:
        PS_orig_action = p_s.select_action(orig_s, other_s, energy)
        p_action = res.select_action(s, energy)
        assert PS_orig_action == p_selector.select_action(orig_s, other_s, energy)
        assert PS_orig_action == p.orig_action(p_action)

for s in [1,3,5]:
    orig_s, other_s = p.components[s]
    try:
        ps_copy.select_action(orig_s, other_s, 100)
        assert False
    except KeyError:
        pass
print("Passed test 3 for ProductSelector in file test_product.py")
# -

# ### LTL selector

# +
f = spot.formula("GF s1 & GF s2")
aut = spot.translate(f, "BA", "deterministic", "complete")
mdp, T = product_example()
lmdp = LCMDP(AP=["s1","s2"], mdp=mdp)
lmdp.state_labels = [set(), {0}, {1}, set()]

capacity = 10
init_energy = 5
# -

# Get ProductSelector
dba_sel = lmdp.selector_for_dba(aut, cap=capacity)

ltl_sel = lmdp.selector_for_ltl("GF s1 & GF s2", cap=capacity)
assert ltl_sel == dba_sel
print("Passed test selector_for_ltl in file test_product.py")

# ### Test DBACounterStrategy

# We create 2 strategies:
#  1. A `CounterStrategy` that works on product CMDP
#  2. A `DBACounterStrategy` that works on labeled CMDP

# Get CounterSelector
product, targets = lmdp.product_with_dba(aut)
psolver = BasicES(product, capacity, targets)
counter_sel = psolver.get_strategy(BUCHI)

from fimdp.strategy import CounterStrategy
from fimdp.labeledConsMDP import DBACounterStategy
cs = CounterStrategy(product, counter_sel, capacity, init_energy)
dbas = DBACounterStategy(lmdp, aut, dba_sel, capacity, init_energy)

# We now start a play from the initial states (0 in both cases) and check whether the strategies give equivalent choices.

for outcome in [0, 2, 3, 0, 2, 3, 0, 1, 4, 5, 4, 5, 6, 3, 0]:
    pr_action = cs.next_action(outcome)
    orig_action = dbas.next_action(product.components[outcome][0])
    assert product.orig_action(pr_action) == orig_action
print("Passed test for DBA strategy in file test_product")
