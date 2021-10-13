"""
Core module defining data structure of FiPOMDP extension of FiMDP.

The core idea is to transform this consumption POMDP into a subset construction (belief support consumption MDP) and
subset construction with guessing (belief support consumption MDP with guessing) and then use already
implemented algorithms with interfacing between the three (CPOMDP, belief supp CMDP, belief supp guess CMDP) constructions
to satisfy safety, positive reachability, and buchi objective for CPOMDP).
#TODO
"""
from typing import List, Dict, Tuple

from fimdp import ConsMDP
from fimdp.distribution import is_distribution


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

    def __init__(self):
        super(ConsPOMDP, self).__init__()

    def set_observations(self, num_observations: int, obs_probs: Dict[Tuple[int, int], float],
                         obs_names: List[str] = None) -> None:
        """
        Set observations to POMDP, and validate their correct format - size, name size, probability distributions
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

        for state, obs in self.obs_probabilities.keys():
            if obs >= num_observations:
                raise AttributeError(
                    f"Observation {obs} does not exist, count of all observation is {self.num_observations}")
            obs_distr = self.state_obs_probs(state)
            if not is_distribution(obs_distr):
                raise AttributeError("Supplied observation dict is not a distribution. The probabilities are:"
                                     f" {list(obs_distr.keys())}, sum: {sum(obs_distr.values())}")

        #TODO check if states in observation match reload property

    def set_name_states(self, names: List[str] = None) -> None:
        """
        Set names for states in order of 'names' parameter
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
        for (state, obs), prob in self.obs_probabilities:
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
        for (state, obs), prob in self.obs_probabilities:
            if obs == given_obs and prob > 0:
                states.append(state)
        return states

    def compute_belief_supp_cmdp(self) -> ConsMDP:
        #TODO doc
        self.structure_change()
        belief_supp_cmdp = ConsMDP()

        return belief_supp_cmdp
