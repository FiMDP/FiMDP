import pytest

from fipomdp.core import ConsPOMDP


def basic():
    m = ConsPOMDP(layout="neato")

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

def basic_explicit():
    m = ConsPOMDP(layout="neato")

    m.new_states(9)
    for s in [0, 7]:
        m.set_reload(s)

    m.add_action(0, {1: 1}, "x", 1)
    m.add_action(1, {0: 1}, "x", 1)
    m.add_action(2, {1: 1}, "x", 1)
    m.add_action(3, {2: .5, 1: .5}, "x", 1)
    m.add_action(3, {4: .5, 6: .5}, "t", 10)
    m.add_action(4, {5: 1}, "t", 1)
    m.add_action(5, {6: 1}, "r", 1)
    m.add_action(6, {3: .5, 7: .5}, "t", 6)
    m.add_action(6, {7: 1}, "r", 1)
    m.add_action(7, {3: 1}, "x", 20)
    m.add_action(7, {6: 1}, "t", 3)
    m.add_action(8, {7: .5, 2: .5}, "x", 5)

    targets = set([2, 5])

    return m, targets


def test_names_not_oflength_num_obs_fail():
    basic_cmdp, basic_targets = basic()

    with pytest.raises(AttributeError,
                       match=r"Length .* of observation names is not same as count of observations .*") as excinfo:
        observation_probabilities = {
            (0, 0): 1,
            (1, 1): 1,
            (2, 2): 1,
            (3, 3): 1,
            (4, 4): 1,
            (5, 5): 1,
            (6, 5): 1,
            (7, 0): 1,
            (8, 5): 1
        }

        names = ['a', 'b']

        basic_cmdp.set_observations(6, observation_probabilities, names)


def test_outofbounds_obs_fail():
    basic_cmdp, basic_targets = basic()

    with pytest.raises(AttributeError,
                       match=r"Observation .* does not exist, count of all observation is .*") as excinfo:
        observation_probabilities = {
            (0, 0): 1,
            (1, 1): 1,
            (2, 2): 1,
            (3, 3): 1,
            (4, 4): 1,
            (5, 5): 1,
            (6, 5): 1,
            (7, 0): 1,
            (8, 5): 0.5,
            (8, 6): 0.5  # 6 out of bounds
        }
        basic_cmdp.set_observations(6, observation_probabilities)


def test_incorrect_distributions_fail():
    basic_cmdp, basic_targets = basic()

    with pytest.raises(AttributeError, match=r"Supplied observation dict is not a distribution. The probabilities "
                                             r"are: .*") as excinfo:
        observation_probabilities = {
            (0, 0): 1,
            (1, 1): 1,
            (2, 2): 1,
            (3, 3): 0.8,  # state 3 observation distribution sums up to 0.8
            (4, 4): 1,
            (5, 5): 1,
            (6, 5): 1,
            (7, 0): 1,
            (8, 5): 1
        }
        basic_cmdp.set_observations(6, observation_probabilities)


def test_empty_observation_fail():
    basic_cmdp, basic_targets = basic()
    with pytest.raises(AttributeError, match=r"No observation should be empty. .*") as excinfo:
        observation_probabilities = {
            (0, 0): 1,
            (1, 2): 1,
            (2, 2): 1,
            (3, 3): 1,
            (4, 4): 1,
            (5, 5): 1,
            (6, 5): 1,
            (7, 0): 1,
            (8, 5): 1
        }
        basic_cmdp.set_observations(6, observation_probabilities)


def test_reloads_nonreloads_in_one_obs_fail():
    basic_cmdp, basic_targets = basic()

    with pytest.raises(AttributeError,
                       match=r"Observations should have the same reload for all belonging states.*") as excinfo:
        observation_probabilities = {
            (0, 0): 1,
            (1, 1): 1,
            (2, 2): 1,
            (3, 3): 1,
            (4, 4): 1,
            (5, 5): 1,  # non-reload in obs 5
            (6, 5): 1,
            (7, 5): 1,  # reload in obs 5
            (8, 5): 1
        }
        basic_cmdp.set_observations(6, observation_probabilities)


def test_set_observations_correct():
    basic_cmdp, basic_targets = basic()

    observation_probabilities = {
        (0, 0): 1,
        (1, 1): 1,
        (2, 2): 1,
        (3, 3): 1,
        (4, 4): 1,
        (5, 4): 0.5,
        (5, 5): 0.5,
        (6, 5): 1,
        (7, 0): 1,
        (8, 5): 1
    }

    basic_cmdp.set_observations(6, observation_probabilities)

    assert basic_cmdp.num_observations == 6, "Setting of observation count failed, should have been 6"
    assert basic_cmdp.obs_probabilities == observation_probabilities, "Setting of observation probabilities failed"

    assert basic_cmdp.obs_states(0) == [0, 7], "Wrong states returned for observation 0, should have been [0, 7]"
    assert basic_cmdp.obs_states(1) == [1], "Wrong states returned for observation 1, should have been [1]"
    assert basic_cmdp.obs_states(2) == [2], "Wrong states returned for observation 2, should have been [2]"
    assert basic_cmdp.obs_states(3) == [3], "Wrong states returned for observation 3, should have been [3]"
    assert basic_cmdp.obs_states(4) == [4, 5], "Wrong states returned for observation 4, should have been [4, 5]"
    assert basic_cmdp.obs_states(5) == [5, 6, 8], "Wrong states returned for observation 5, should have been [5, 6, 8]"

    assert basic_cmdp.state_obs_probs(0) == {0: 1}, "Wrong observation : probability dict return for state 0, should have been {0: 1}"
    assert basic_cmdp.state_obs_probs(1) == {1: 1}, "Wrong observation : probability dict return for state 1, should have been {1: 1}"
    assert basic_cmdp.state_obs_probs(2) == {2: 1}, "Wrong observation : probability dict return for state 2, should have been {2: 1}"
    assert basic_cmdp.state_obs_probs(3) == {3: 1}, "Wrong observation : probability dict return for state 3, should have been {3: 1}"
    assert basic_cmdp.state_obs_probs(4) == {4: 1}, "Wrong observation : probability dict return for state 4, should have been {4: 1}"
    assert basic_cmdp.state_obs_probs(5) == {4: 0.5, 5: 0.5}, "Wrong observation : probability dict return for state 0, should have been {4: 0.5, 5: 0.5}"
    assert basic_cmdp.state_obs_probs(6) == {5: 1}, "Wrong observation : probability dict return for state 6, should have been {5: 1}"
    assert basic_cmdp.state_obs_probs(7) == {0: 1}, "Wrong observation : probability dict return for state 7, should have been {0: 1}"
    assert basic_cmdp.state_obs_probs(8) == {5: 1}, "Wrong observation : probability dict return for state 8, should have been {5: 1}"

def test_bel_supp_compute():
    basic_cmdp, basic_targets = basic_explicit()

    observation_probabilities = {
        (0, 0): 1,
        (1, 1): 1,
        (2, 2): 1,
        (3, 3): 1,
        (4, 4): 1,
        (5, 5): 1,
        (6, 5): 1,
        (7, 0): 1,
        (8, 5): 1
    }

    basic_cmdp.set_observations(6, observation_probabilities)

    basic_cmdp.compute_belief_supp_cmdp()












