from fimdp.products import DBAWrapper

import spot

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
