"""
Core module defining data structure of FiPOMDP extension of FiMDP.

The core idea is to transform this consumption POMDP into a subset construction (belief support consumption MDP) and
subset construction with guessing (belief support consumption MDP with guessing) and then use already
implemented algorithms with interfacing between the three (CPOMDP, belief supp CMDP, belief supp guess CMDP) constructions
to satisfy safety, positive reachability, and buchi objective for CPOMDP).
#TODO
"""
from functools import reduce
from itertools import groupby
from typing import List, Dict, Tuple

from fimdp import ConsMDP
from fimdp.core import ActionData
from fimdp.distribution import is_distribution
from .pomdp_factories import power_set


class ConsPOMDP(ConsMDP):
    """
    Representation of partially observable Markov Decision Processes with consumption on actions

    Extending ConsMDP, we represent observations by integers (with possible names in 'observation_names').

    Observations are represented as a Map of (state, observation) tuple and probability.
    """

    num_observations: int
    observation_names: List[str] or None
    obs_probabilities: Dict[Tuple[int, int], float]

    belief_supp_cmdp: ConsMDP
    belief_supp_guess_cmdp: ConsMDP

    def __init__(self, layout=None):
        super(ConsPOMDP, self).__init__(layout)

    def set_observations(self, num_observations: int, obs_probs: Dict[Tuple[int, int], float],
                         obs_names: List[str] = None) -> None:
        """
        Set observations to POMDP, and validate their correct format - size, name size, probability distributions,
        same reloads in observation
        Parameters
        ----------
        num_observations - number of all observations
        obs_probs - distribution of (state, observation) probabilities
        obs_names - names of observations
        -------
        """

        if obs_names is not None and len(obs_names) != num_observations:
            raise AttributeError(f"Length ({len(obs_names)}) of observation names is not same "
                                 f"as count of observations ({num_observations}).")

        self.structure_change()
        self.num_observations = num_observations
        self.observation_names = obs_names
        self.obs_probabilities = obs_probs

        for obs in range(num_observations):
            states = self.obs_states(obs)
            if len(states) == 0:
                # check that all observations are not empty
                raise AttributeError(
                    f"No observation should be empty. Observation {obs} is empty.")

        for state, obs in self.obs_probabilities.keys():
            if obs >= num_observations:
                # check that observation indices in given distribution dict are not higher than allowed index
                raise AttributeError(
                    f"Observation {obs} does not exist, count of all observation is {self.num_observations}")
            obs_distr = self.state_obs_probs(state)
            if not is_distribution(obs_distr):
                # check that distributions add up to 1
                raise AttributeError("Supplied observation dict is not a distribution. The probabilities are:"
                                     f" {list(obs_distr.keys())}, sum: {sum(obs_distr.values())}")
            reloads = [self.reloads[i] for i in states]
            if len(set(reloads)) != 1:
                # check that reload property for observation states match
                raise AttributeError(
                    f"Observations should have the same reload for all belonging states. Observation {obs} doesn't.")

    def set_state_names(self, names: List[str] = None) -> None:
        """
        Set names for states in order of 'names' parameter or give their number as index
        Parameters
        ----------
        names List of names for states, defaults to None
        -------
        """
        self.structure_change()
        if self.names is None and names is None:
            self.names = [str(x) for x in range(self.num_states)]
        else:
            if len(names) != self.num_states:
                raise AttributeError(
                    f"Names: {names} aren't the same length as is the number of states: {self.num_states}.")
            else:
                self.names = names

    def set_obs_names(self, names: List[str] = None) -> None:
        """
        Set names for observations
        Parameters
        ----------
        names

        Returns
        -------

        """
        self.structure_change()
        if self.observation_names is None and names is None:
            self.observation_names = [str(x) for x in range(self.num_observations)]
        else:
            if len(names) != self.observation_names:
                raise AttributeError(
                    f"Names: {names} aren't the same length as is the number of observations: {self.num_observations}.")
            else:
                self.observation_names = names

    def state_obs_probs(self, given_state: int) -> Dict[int, float]:
        """
        Get observation probabilities for given state
        Parameters
        ----------
        given_state - given state index

        Returns Distribution of observation probabilities for all probabilities >0
        -------
        """
        if given_state >= self.num_states:
            raise AttributeError(f"State {given_state} does not exist, count of all states is {self.num_states}")
        state_obs_probs = {}
        for (state, obs), prob in self.obs_probabilities.items():
            if state == given_state:
                state_obs_probs[obs] = prob
        return state_obs_probs

    def obs_states(self, given_obs: int) -> List[int]:
        """
        Get all states that have a probability >0 of appearing in the observation
        Parameters
        ----------
        given_obs given observation index

        Returns List of all states possible for observation
        -------

        """
        if given_obs >= self.num_observations:
            raise AttributeError(
                f"Observation {given_obs} does not exist, count of all observation is {self.num_observations}")
        states = []
        for (state, obs), prob in self.obs_probabilities.items():
            if obs == given_obs and prob > 0:
                states.append(state)
        return states

# TODO bel_supp with initial state

    def compute_belief_supp_cmdp(self) -> None:
        # TODO doc
        self.structure_change()
        if self.names is None:
            self.set_state_names()  # Set indices as state names

        belief_supp_cmdp = BeliefSuppConsMDP(self)
        for obs_i in range(self.num_observations):
            obs_i_states = self.obs_states(obs_i)
            subsets = power_set(obs_i_states)
            subsets.remove([])  # No need for empty belief support
            reload = self.is_reload(obs_i_states[0])
            for subset in subsets:
                # print("SUBSET_________________"+str(subset))
                if len(subset) == 1:
                    name = "bel_supp_" + str(subset[0])
                else:
                    name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", subset)
                belief_supp_cmdp.new_state(obs_i, reload, name, subset)

        for belief_supp in belief_supp_cmdp.belief_supports:
            print("BEL_SUPP______________", belief_supp)
            belief_supp_actions = []
            for supp_state in belief_supp:
                supp_state_actions = self.actions_for_state(supp_state)
                for action in supp_state_actions:
                    belief_supp_actions.append(action)
                # print(len(belief_supp_actions))
            for label, grouped_actions in groupby(belief_supp_actions, lambda act: act.label):
                # print(str(belief_supp) + label)
                bel_supp_labeled_acts = list(grouped_actions)
                print("LABELED_ACTIONS____", bel_supp_labeled_acts)
                self.add_belief_supp_action(belief_supp, label, bel_supp_labeled_acts, belief_supp_cmdp)

        self.belief_supp_cmdp = belief_supp_cmdp

    def add_belief_supp_action(self, belief_src: List[int], label: str, bel_supp_actions: List[ActionData],
                               bel_supp_cmdp: ConsMDP) -> None:
        # TODO doc
        cons = bel_supp_actions[0].cons  # IMPORTANT expecting energy observability
        src_state = bel_supp_cmdp.belief_supports.index(belief_src)
        dest_distribution = {}
        dest_states = []

        act_distrs = []
        for action in bel_supp_actions:
            act_distrs.extend(list(action.distr.items()))
        for obs_distr, same_obs_distrs_groups in groupby(act_distrs, lambda distr: self.state_obs_probs(distr[0])):
            groups_list = list(same_obs_distrs_groups)
            print("OBS_DISTR", obs_distr)
            for obs, prob in obs_distr.items():
                print("GROUPS" + str(groups_list))
                print(len(groups_list))
                obs_weight = prob
                belief_dest = []
                act_weight = 0
                number_of_act_weights = 0
                for group in groups_list:
                    belief_dest.append(group[0])
                    act_weight += group[1]
                    number_of_act_weights += 1
                    print()
                belief_dest.sort()
                dest_states.append(bel_supp_cmdp.belief_supports.index(belief_dest))
                dest_distribution[bel_supp_cmdp.belief_supports.index(belief_dest)] = (obs_weight * act_weight) / number_of_act_weights
        dest_distribution = {k: v/len(dest_distribution) for k, v in dest_distribution.items()}
        bel_supp_cmdp.add_action(src_state, dest_distribution, label, cons)


class BeliefSuppConsMDP(ConsMDP):
    # TODO doc
    original_cpomdp: ConsPOMDP
    belief_supports: List[List[int]]
    original_observations: List[int]

    def __init__(self, original_cpomdp: ConsPOMDP):
        super(BeliefSuppConsMDP, self).__init__()
        self.original_cpomdp = original_cpomdp
        self.original_observations = []
        self.belief_supports = []

    def new_state(self, original_obs: int, reload: bool = False, name: str = None, belief_support: List[int] = []):
        super(BeliefSuppConsMDP, self).new_state(reload, name)
        self.original_observations.append(original_obs)
        self.belief_supports.append(belief_support)

    def new_states(self, original_obs: int, count, names=None, belief_supports=None):
        super(BeliefSuppConsMDP, self).new_states(count, names)
        self.belief_supports.extend(belief_supports)
        self.original_observations.extend([original_obs for _ in range(count)])
