from reachability_examples import ultimate
import fimdp.explicit as mec

mdp = ultimate()[0]
result = mec.get_MECs(mdp)
expected = [[2, 1], [9], [8, 6, 4, 5, 3]]
mdp.show()

assert result == expected, ("get_MECs() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_MECs() in test_mecs file.")
