from typing import Set, List, Dict, Tuple

from fimdp import ConsMDP
from fimdp.distribution import is_distribution


class ConsPOMDP(ConsMDP):

    observations: Set[str]
    obs_probabilities: Dict[Tuple[int, int], float]

    def __init__(self):
        super(ConsPOMDP, self).__init__()

    def set_observations(self, observations: Set[str], obs_probs: Dict[Tuple[int, int], float]) -> None:
        self.observations = observations
        self.obs_probabilities = obs_probs

        for state in obs_probs.keys():
            obs_distr = obs_probs[state]
            if not is_distribution(obs_distr):
                raise AttributeError("Supplied observation dict is not a distribution." +
                                     " The probabilities are: {}, sum: {}".format
                                     (list(obs_distr[1]),
                                      sum(obs_distr[1])))


    def get_same_state_obs_probs(self) -> Dict[int, Dict[int, float]]:
        same_state_obs_probs = {self.num_states}
        for (state, obs), prob in self.obs_probabilities:
            if state in same_state_obs_probs.keys():
                same_state_obs_probs[state] = same_state_obs_probs.get(state)
        return same_state_obs_probs

    def get_obs_distribution(self, state : int) -> Tuple[int, float]:
        return self.observations[state]

    def compute_belief_supp_CMDP(self) -> ConsMDP:
        pass #TODO



