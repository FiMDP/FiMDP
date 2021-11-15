"""
Core module defining data structure of FiPOMDP extension of FiMDP.

The core idea is to transform this consumption POMDP into a subset construction (belief support consumption MDP) and
subset construction with guessing (belief support consumption MDP with guessing) and then use already
implemented algorithms with interfacing between the three (CPOMDP, belief supp CMDP, belief supp guess CMDP) constructions
to satisfy safety, positive reachability, and buchi objective for CPOMDP).
# TODO
"""
from collections import deque
from functools import reduce
from itertools import groupby
from typing import List, Dict, Tuple

from fimdp import ConsMDP
from fimdp.core import ActionData
from fimdp.distribution import is_distribution, uniform


class BeliefSuppConsMDP(ConsMDP):
    """
    Representation of Belief Support consumption MDPs, which are derived from consumption POMDPs

    This representation uses subsets of all states in observation (belief supports)
    to get rid of uncertainties in POMDPs

    This class extends ConsMDP

    This class stores belief supports as Lists in a List indexed by state numbers
    """
    bel_supps: List[List[int]]

    def __init__(self):
        super(BeliefSuppConsMDP, self).__init__()
        self.bel_supps = []

    def new_state(self, reload: bool = False, name: str = None, belief_support: List[int] = []):
        super(BeliefSuppConsMDP, self).new_state(reload, name)
        self.bel_supps.append(belief_support)

    def new_states(self, count, names=None, belief_supports=None):
        super(BeliefSuppConsMDP, self).new_states(count, names)
        self.bel_supps.extend(belief_supports)


class GuessingConsMDP(BeliefSuppConsMDP):
    """
    Representation of Belief Support consumption MDP with guessing, which can be derived from consumption POMDPs

    This class extends BeliefSuppConsMDP

    Guesses for each state are of type int (None) and are kept in list indexed by state numbers
    """
    guesses: List[int]

    def __init__(self):
        super(GuessingConsMDP, self).__init__()
        self.guesses = []

    def new_state(self, reload: bool = False, name: str = None, belief_support: List[int] = [], guess: int = None):
        if guess is not None and guess not in belief_support:
            raise AttributeError(f"Supplied guess {guess} does not match with supplied belief support {belief_support}.")
        super(GuessingConsMDP, self).new_state(reload, name, belief_support)
        self.guesses.append(guess)


class ConsPOMDP(ConsMDP):
    """
    Representation of partially observable Markov Decision Processes with consumption on actions

    Extending ConsMDP, we represent observations by integers (with possible names in 'observation_names').

    Observations are represented as a Map of (state, observation) tuple and probability.
    """

    num_observations: int
    observation_names: List[str] or None
    obs_probabilities: Dict[Tuple[int, int], float]

    belief_supp_cmdp: BeliefSuppConsMDP
    guessing_cmdp: GuessingConsMDP

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

    def compute_belief_supp_cmdp_initial_state(self, initial_belief_supp: List[int]) -> None:
        self.structure_change()
        belief_supp_cmdp = BeliefSuppConsMDP()
        queue = deque()
        queue.append(initial_belief_supp)
        if len(initial_belief_supp) == 1:
            name = "bel_supp_" + str(initial_belief_supp[0])
        else:
            name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", initial_belief_supp)
        belief_supp_cmdp.new_state(self.reloads[initial_belief_supp[0]], name, initial_belief_supp)
        while len(queue) > 0:
            belief_support = queue.popleft()
            state_actions = []
            for supp_state in belief_support:
                for action in self.actions_for_state(supp_state):
                    state_actions.append(action)
            self._bfs_add_belief_supp_action(belief_support, state_actions, belief_supp_cmdp, queue)
        self.belief_supp_cmdp = belief_supp_cmdp

    def _bfs_add_belief_supp_action(self, belief_src: List[int], bel_supp_state_actions: List[ActionData],
                                    bel_supp_cmdp: BeliefSuppConsMDP, queue: deque):
        bel_supp_state_actions.sort(key=lambda act: act.label)
        for label, action_groups in groupby(bel_supp_state_actions, lambda act: act.label):
            print("\nBELIEF_SUPP" + str(belief_src) + label)
            bel_supp_labeled_acts = list(action_groups)
            print("LABELED_ACTIONS____", bel_supp_labeled_acts)
            self._add_belief_supp_action_with_label(belief_src, label, bel_supp_labeled_acts, bel_supp_cmdp, queue)

    def _add_belief_supp_action_with_label(self, belief_src: List[int], label: str, bel_supp_actions_same_label: List[ActionData],
                                           bel_supp_cmdp: BeliefSuppConsMDP, queue: deque = None) -> None:
        """

        Parameters
        ----------
        belief_src
        label
        bel_supp_actions_same_label
        bel_supp_cmdp

        Returns
        -------

        """
        cons = bel_supp_actions_same_label[0].cons  # IMPORTANT expecting energy observability
        src_state = bel_supp_cmdp.bel_supps.index(belief_src)
        dest_states = []

        act_distrs = []
        for action in bel_supp_actions_same_label:
            act_distrs.extend(list(action.distr.items()))
        for obs_distr, same_obs_distrs_groups in groupby(act_distrs, lambda distr: self.state_obs_probs(distr[0])):
            groups_list = list(same_obs_distrs_groups)
            print("OBS_DISTR", obs_distr)
            for obs, prob in obs_distr.items():
                print("GROUPS" + str(groups_list))
                belief_dest = []
                for group in groups_list:
                    belief_dest.append(group[0])
                belief_dest.sort()
                if queue is not None and belief_dest not in bel_supp_cmdp.bel_supps:
                    if len(belief_dest) == 1:
                        name = "bel_supp_" + str(belief_dest[0]) + "__obs" + str(obs)
                    else:
                        name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", belief_dest) + "__obs" + str(obs)
                    bel_supp_cmdp.new_state(self.reloads[belief_dest[0]], name, belief_dest)
                    queue.append(belief_dest)
                dest_states.append(bel_supp_cmdp.bel_supps.index(belief_dest))
        dest_distribution = uniform(list(set(dest_states)))
        bel_supp_cmdp.add_action(src_state, dest_distribution, label, cons)

    def compute_guessing_cmdp_initial_state(self, initial_belief: List[int], initial_guess: int) -> None:
        self.structure_change()
        self.compute_belief_supp_cmdp_initial_state(initial_belief)
        guessing_cmpd = GuessingConsMDP()
        if len(initial_belief) == 1:
            name = "bel_supp_" + str(initial_belief[0]) + "__guess" + str(initial_guess)
        else:
            name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", initial_belief) + "__guess" + str(initial_guess)
        guessing_cmpd.new_state(self.reloads[initial_belief[0]], name, initial_belief, initial_guess)
        queue = deque()
        queue.append((initial_belief, initial_guess))
        while len(queue) > 0:
            belief, guess = queue.popleft()
            self._bfs_add_guess_cmdp_actions(belief, guess, guessing_cmpd, queue)
        self.guessing_cmdp = guessing_cmpd

    def _bfs_add_guess_cmdp_actions(self, src_belief_supp: List[int], src_guess: int, guessing_cmdp: GuessingConsMDP, queue: deque):
        bel_supp_index = self.belief_supp_cmdp.bel_supps.index(src_belief_supp)
        src_state = list(zip(guessing_cmdp.bel_supps, guessing_cmdp.guesses)).index((src_belief_supp, src_guess))
        for bel_supp_action in self.belief_supp_cmdp.actions_for_state(bel_supp_index):

            dest_states = []

            if src_guess is None:
                succ_bel_supps = list(
                    map(lambda succ: self.belief_supp_cmdp.bel_supps[succ], bel_supp_action.get_succs()))
                for succ_bel_supp in succ_bel_supps:
                    if (succ_bel_supp, None) not in list(zip(guessing_cmdp.bel_supps, guessing_cmdp.guesses)):
                        reload = self.belief_supp_cmdp.reloads[self.belief_supp_cmdp.bel_supps.index(succ_bel_supp)]
                        if len(succ_bel_supp) == 1:
                            name = "bel_supp_" + str(succ_bel_supp[0]) + "__guess" + str(None)
                        else:
                            name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", succ_bel_supp) + "__guess" + str(None)
                        guessing_cmdp.new_state(reload, name, succ_bel_supp, None)
                        queue.append((succ_bel_supp, None))
                    guessing_states = list(zip(guessing_cmdp.bel_supps, guessing_cmdp.guesses))
                    dest_states.append(guessing_states.index((succ_bel_supp, None)))
                guessing_cmdp.add_action(src_state, uniform(dest_states), bel_supp_action.label, bel_supp_action.cons)
                continue

            match_label_actions = []
            for state_action in self.actions_for_state(src_guess):
                if state_action.label == bel_supp_action.label:
                    match_label_actions.append(state_action)
            succ_bel_supps = list(map(lambda succ: self.belief_supp_cmdp.bel_supps[succ], bel_supp_action.get_succs()))
            for label_action in match_label_actions:
                for bel_supp in succ_bel_supps:
                    guesses = []
                    for bel_supp_state in bel_supp:
                        if bel_supp_state in label_action.get_succs():
                            guesses.append(bel_supp_state)
                    if len(guesses) == 0:
                        guesses.append(None)
                    for guess in guesses:
                        if (bel_supp, guess) not in list(zip(guessing_cmdp.bel_supps, guessing_cmdp.guesses)):
                            reload = self.belief_supp_cmdp.reloads[self.belief_supp_cmdp.bel_supps.index(bel_supp)]
                            if len(bel_supp) == 1:
                                name = "bel_supp_" + str(bel_supp[0]) + "__guess" + str(guess)
                            else:
                                name = "bel_supp_" + reduce(lambda x, y: f"{x}_{y}", bel_supp) + "__guess" + str(guess)
                            guessing_cmdp.new_state(reload, name, bel_supp, guess)
                            queue.append((bel_supp, guess))
                        guessing_states = list(zip(guessing_cmdp.bel_supps, guessing_cmdp.guesses))
                        dest_states.append(guessing_states.index((bel_supp, guess)))
            guessing_cmdp.add_action(src_state, uniform(dest_states), bel_supp_action.label, bel_supp_action.cons)


