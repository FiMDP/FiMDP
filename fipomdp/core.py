"""
Core module defining data structure of FiPOMDP extension of FiMDP.

The core idea is to transform this consumption POMDP into a subset construction (belief support consumption MDP) and
subset construction with guessing (belief support consumption MDP with guessing) and then use already
implemented algorithms with interfacing between the three (CPOMDP, belief supp CMDP, belief supp guess CMDP) constructions
to satisfy safety, positive reachability, and buchi objective for CPOMDP).
The representation in this module assumes energy observability - action consumption depends on observation.

Classes in this module - BeliefSuppConsMDP, GuessingConsMDP, ConsPOMDP
"""
from collections import deque
from itertools import groupby
from typing import Dict, List, Optional, Tuple

from fimdp import ConsMDP
from fimdp.core import ActionData
from fimdp.distribution import is_distribution, uniform
from fipomdp.pomdp_factories import bel_supp_guess_state_name, bel_supp_state_name


class BeliefSuppConsMDP(ConsMDP):
    """Representation of Belief Support consumption MDPs, which are derived from consumption POMDPs.

    This representation uses subsets of all states in observation (belief supports)
    to get rid of uncertainties in POMDPs.

    This class extends ConsMDP.

    This class stores belief supports as Lists in a List indexed by state numbers.

    Attributes
    ----------
    bel_supps : List[List[int]]
        List of belief supports
    bel_supp_indexer : Dict[Tuple[int, ...], int]
        Dict with belief supports as keys and their state number as value, for faster finding of state index.
    """

    bel_supps: List[List[int]]
    bel_supp_indexer: Dict[Tuple[int, ...], int]

    def __init__(self):
        super(BeliefSuppConsMDP, self).__init__()
        self.bel_supps = []
        self.bel_supp_indexer = {}

    def new_state(
        self, belief_support: List[int], reload: bool = False, name: str = None
    ) -> None:
        super(BeliefSuppConsMDP, self).new_state(reload, name)
        self.bel_supps.append(belief_support)
        self.bel_supp_indexer[tuple(belief_support)] = self.num_states - 1


class GuessingConsMDP(ConsMDP):
    """Representation of Belief Support consumption MDP with guessing, which can be derived from consumption POMDPs.

    This class extends ConsMDP.

    Guesses for each state are of type int (None) and are kept in list indexed by state numbers.

    Attributes
    ----------
    belief_supp_guess_pairs : List[Tuple[List[int], Optional[int]]]
        List of guesses, which can be None, None representing empty guess (epsilon)
    bel_supp_guess_indexer : Dict[Tuple[Tuple[int, ...], Optional[int]], int]
        Dict with belief support and guess tuples as keys, and state numbers as values,
        for faster finding of state index.
    """

    belief_supp_guess_pairs: List[Tuple[List[int], Optional[int]]]
    bel_supp_guess_indexer: Dict[Tuple[Tuple[int, ...], Optional[int]], int]

    def __init__(self):
        super(GuessingConsMDP, self).__init__()
        self.belief_supp_guess_pairs = []
        self.bel_supp_guess_indexer = {}

    def new_state(
        self,
        belief_support: List[int],
        reload: bool = False,
        name: str = None,
        guess: Optional[int] = None,
    ) -> None:
        if guess is not None and guess not in belief_support:
            raise AttributeError(
                f"Supplied guess {guess} does not match with supplied belief support {belief_support}."
            )

        super(GuessingConsMDP, self).new_state(reload, name)
        self.belief_supp_guess_pairs.append((belief_support, guess))
        self.bel_supp_guess_indexer[(tuple(belief_support), guess)] = (
            self.num_states - 1
        )

    def belief_supp_states(self, belief_supp: List[int]) -> List[int]:
        return list(
            filter(
                lambda state: self.belief_supp_guess_pairs[state][0] == belief_supp,
                range(self.num_states),
            )
        )


class ConsPOMDP(ConsMDP):
    """Representation of partially observable Markov Decision Processes with consumption on actions.

    Extending ConsMDP, we represent observations by integers (with possible names in 'observation_names').

    Observations are represented as a Map of (state, observation) tuple and probability.

    Attributes
    ----------
    num_observations : int
        Number of all observations.
    observation_names : Optional[List[str]]
        Names of observations, list should always be the same length as num_observations, names are optional.
    obs_probabilities : Dict[Tuple[int, int], float]
        Observation-Probability dictionary, tuples of states and observations are linked to probability values.
        Probabilities for each state should always add up to one.

    belief_supp_cmdp : BeliefSuppConsMDP
        Belief support consumption MDP, this cmdp is computable only via compute_belief_supp_... function call,
        and will always be computed with initial state, to increase performance.
    guessing_cmdp : GuessingConsMDP
        Belief support consumption MDP with guessing, similar to belief_supp_cmdp, this cmdp is computable only via
        compute_guessing_... function call, and will always be computed with initial state and initial guess.
    """

    num_observations: int
    observation_names: Optional[List[str]]
    obs_probabilities: Dict[Tuple[int, int], float]

    belief_supp_cmdp: BeliefSuppConsMDP
    guessing_cmdp: GuessingConsMDP

    def __init__(self, layout=None):
        super(ConsPOMDP, self).__init__(layout)

    def set_observations(
        self,
        num_observations: int,
        obs_probs: Dict[Tuple[int, int], float],
        obs_names: Optional[List[str]] = None,
    ) -> None:
        """Set observations to POMDP, and validate their correct format - size, name size, probability distributions,
        same reloads in observation.

        Parameters
        ----------
        num_observations : int
            Number of all observations.
        obs_probs : Dict[Tuple[int, int], float]
            Distribution of (state, observation) probabilities.
        obs_names : Optional[List[str]]
            Names of observations, optional.
        -------
        """
        if obs_names is not None and len(obs_names) != num_observations:
            raise AttributeError(
                f"Length ({len(obs_names)}) of observation names is not same "
                f"as count of observations ({num_observations})."
            )

        self.structure_change()
        self.num_observations = num_observations
        self.observation_names = obs_names
        self.obs_probabilities = obs_probs

        for obs in range(num_observations):
            states = self.get_obs_states(obs)
            if len(states) == 0:
                # check that all observations are not empty
                raise AttributeError(
                    f"No observation should be empty. Observation {obs} is empty."
                )

            reloads = [self.reloads[i] for i in states]
            if len(set(reloads)) != 1:
                # check that reload property for observation states match
                raise AttributeError(
                    f"Observations should have the same reload for all belonging states. Observation {obs} doesn't."
                )

        for state, obs in self.obs_probabilities.keys():
            if obs >= num_observations:
                # check that observation indices in given distribution dict are not higher than allowed index
                raise AttributeError(
                    f"Observation {obs} does not exist, count of all observation is {self.num_observations}"
                )

            obs_distr = self.get_state_obs_probs(state)
            if not is_distribution(obs_distr):
                # check that distributions add up to 1
                raise AttributeError(
                    "Supplied observation dict is not a distribution. The probabilities are:"
                    f" {list(obs_distr.keys())}, sum: {sum(obs_distr.values())}"
                )

    def set_state_names(self, names: Optional[List[str]] = None) -> None:
        """
        Set names for states in order of 'names' parameter or give their number as index
        Parameters
        ----------
        names : Optional[List[str]]
            Optional given state names.
        -------
        """
        self.structure_change()
        if self.names is None and names is None:
            self.names = list(map(str, range(self.num_states)))
            return

        if len(names) != self.num_states:
            raise AttributeError(
                f"Names: {names} aren't the same length as is the number of states: {self.num_states}."
            )

        self.names = names

    def set_obs_names(self, observation_names: Optional[List[str]] = None) -> None:
        """Set names for observations.

        Parameters
        ----------
        observation_names : Optional[List[str]]
            Optional given observation names.
        """

        self.structure_change()
        if self.observation_names is None and observation_names is None:
            self.observation_names = list(map(str, range(self.num_observations)))
            return

        if len(observation_names) != self.observation_names:
            raise AttributeError(
                f"Names: {observation_names} aren't the same length as is the number of observations: {self.num_observations}."
            )

        self.observation_names = observation_names

    def get_state_obs_probs(self, given_state: int) -> Dict[int, float]:
        """Get observation probabilities for given state with probability >0 .

        Parameters
        ----------
        given_state : int
            Given state index.

        Returns
        -------
        Dict[int, float]
            Distribution of observation probabilities for state.
        """

        if given_state >= self.num_states:
            raise AttributeError(
                f"State {given_state} does not exist, count of all states is {self.num_states}"
            )

        return dict(
            (ko, prob)
            for ((ks, ko), prob) in self.obs_probabilities.items()
            if ks == given_state
        )

    def get_obs_states(self, given_obs: int) -> List[int]:
        """Get all states that have a probability >0 of appearing in the observation.

        Parameters
        ----------
        given_obs : int
            Given observation index.

        Returns
        -------
        List[int]
            List of all states in observation.
        """

        if given_obs >= self.num_observations:
            raise AttributeError(
                f"Observation {given_obs} does not exist, count of all observation is {self.num_observations}"
            )

        return list(
            ks
            for ((ks, ko), prob) in self.obs_probabilities.items()
            if ko == given_obs and prob > 0
        )

    def get_states_obss_possible(self, states: List[int]) -> List[int]:
        """Get all observations that are possible for a list of states.
        Parameters
        ----------
        states : List[int]
            List of states.

        Returns
        -------
        List[int]
            List of all observations possible for given states.
        """

        obss = set({})
        for state in states:
            for obs in self.get_state_obs_probs(state).keys():
                obss.add(obs)

        return list(obss)

    def get_bel_supps_for_states(self, states: List[int]) -> List[List[int]]:
        belief_supps = []

        for obs in self.get_states_obss_possible(states):
            intersect = sorted(set(self.get_obs_states(obs)).intersection(states))
            if len(intersect) != 0:
                belief_supps.append(intersect)

        return belief_supps

    def compute_belief_supp_cmdp_initial_state(
        self, initial_belief_supp: List[int]
    ) -> None:
        """For given initial belief support, compute corresponding belief support cmdp from this cpomdp instance.
        This computation traverses the graph in BFS like way.

        For each belief support encountered in queue groups actions by labels and then for each state in that belief
        support finds all successor states, which then are grouped into belief supports themselves, and pushed into the
        queue if its the first time finding such belief supports.

        Parameters
        ----------
        initial_belief_supp : List[int]
            Initial belief support, should not be empty
        """

        if len(initial_belief_supp) == 0:
            raise AttributeError(
                f"Initial belief support {initial_belief_supp} should not be empty!"
            )

        self.structure_change()
        belief_supp_cmdp = BeliefSuppConsMDP()

        queue = deque()
        queue.append(initial_belief_supp)

        name = bel_supp_state_name(initial_belief_supp)

        belief_supp_cmdp.new_state(
            initial_belief_supp, self.reloads[initial_belief_supp[0]], name
        )
        while len(queue) > 0:
            belief_support = queue.popleft()
            state_actions = []
            for supp_state in belief_support:
                for action in self.actions_for_state(supp_state):
                    state_actions.append(action)
            self._bfs_add_belief_supp_action(
                belief_support, state_actions, belief_supp_cmdp, queue
            )

        self.belief_supp_cmdp = belief_supp_cmdp

    def _bfs_add_belief_supp_action(
        self,
        belief_src: List[int],
        bel_supp_state_actions: List[ActionData],
        bel_supp_cmdp: BeliefSuppConsMDP,
        queue: deque,
    ):
        bel_supp_state_actions.sort(key=lambda act: act.label)
        for label, action_groups in groupby(
            bel_supp_state_actions, lambda act: act.label
        ):
            bel_supp_labeled_acts = list(action_groups)
            self._add_belief_supp_action_with_label(
                belief_src, label, bel_supp_labeled_acts, bel_supp_cmdp, queue
            )

    def _add_belief_supp_action_with_label(
        self,
        belief_src: List[int],
        label: str,
        bel_supp_actions_same_label: List[ActionData],
        bel_supp_cmdp: BeliefSuppConsMDP,
        queue: deque = None,
    ) -> None:

        cons = bel_supp_actions_same_label[
            0
        ].cons  # IMPORTANT expecting energy observability
        src_state = bel_supp_cmdp.bel_supp_indexer[tuple(belief_src)]
        bs_cmdp_dest_states = []
        act_destinations = []

        for action in bel_supp_actions_same_label:
            act_destinations.extend(action.distr.keys())

        for belief_dest in self.get_bel_supps_for_states(act_destinations):
            belief_dest.sort()
            if (
                queue is not None
                and tuple(belief_dest) not in bel_supp_cmdp.bel_supp_indexer.keys()
            ):
                name = bel_supp_state_name(belief_dest)
                bel_supp_cmdp.new_state(belief_dest, self.reloads[belief_dest[0]], name)
                queue.append(belief_dest)

            bs_cmdp_dest_states.append(
                bel_supp_cmdp.bel_supp_indexer[tuple(belief_dest)]
            )
        dest_distribution = uniform(list(set(bs_cmdp_dest_states)))
        bel_supp_cmdp.add_action(src_state, dest_distribution, label, cons)

    def compute_guessing_cmdp_initial_state(self, initial_belief: List[int]) -> None:
        """For given initial belief support and all its guesses, compute corresponding belief support cmdp with guessing
        from this cpomdp instance.
        This computation traverses the graph in BFS like way.

        For each belief support and guess pair which is in the queue, the following happens.
        Firstly if the guess is None, all actions from belief support cmdp are mapped into guessing cmdp with None guess
        in successors.
        If the guess isn't None, belief support actions for given belief support are compared with cpomdp actions for
        state of given guess and for each successor belief support if there are possible guesses, actions from source
        belief support and guess to destination belief support and guesses are created, otherwise for that successor
        belief support, action from source belief support and guess to that belief support and None guess is created.
        In both cases, pairs of belief support and guess are added to queue if they haven't been visited yet.

        Parameters
        ----------
        initial_belief : List[int]
            Initial belief support
        """

        self.structure_change()
        self.compute_belief_supp_cmdp_initial_state(initial_belief)

        guessing_cmpd = GuessingConsMDP()

        name = bel_supp_state_name(initial_belief)
        queue = deque()

        for initial_guess in initial_belief:
            guessing_cmpd.new_state(
                initial_belief, self.reloads[initial_belief[0]], name, initial_guess
            )
            queue.append((initial_belief, initial_guess))

        while len(queue) > 0:
            belief, guess = queue.popleft()
            self._bfs_add_guess_cmdp_actions(belief, guess, guessing_cmpd, queue)

        self.guessing_cmdp = guessing_cmpd

    def _bfs_add_guess_cmdp_actions(
        self,
        src_belief_supp: List[int],
        src_guess: int,
        guessing_cmdp: GuessingConsMDP,
        queue: deque,
    ):
        bel_supp_index = self.belief_supp_cmdp.bel_supp_indexer[
            (tuple(src_belief_supp))
        ]
        src_state = guessing_cmdp.bel_supp_guess_indexer[
            (tuple(src_belief_supp), src_guess)
        ]

        for bel_supp_action in self.belief_supp_cmdp.actions_for_state(bel_supp_index):
            dest_states = []

            succ_bel_supps = [
                self.belief_supp_cmdp.bel_supps[succ]
                for succ in bel_supp_action.get_succs()
            ]

            if src_guess is None:
                dest_states = [
                    self._process_guess_destination_state(
                        succ_bel_supp, None, guessing_cmdp, queue
                    )
                    for succ_bel_supp in succ_bel_supps
                ]

                guessing_cmdp.add_action(
                    src_state,
                    uniform(dest_states),
                    bel_supp_action.label,
                    bel_supp_action.cons,
                )
                continue

            label = bel_supp_action.label
            match_label_actions = filter(
                lambda action: action.label == label, self.actions_for_state(src_guess)
            )

            for label_action in match_label_actions:
                label_action_succs = label_action.get_succs()
                for bel_supp in succ_bel_supps:
                    guesses = filter(
                        lambda bel_supp_state: bel_supp_state in label_action_succs,
                        bel_supp,
                    )

                    empty_guesses = True

                    for guess in guesses:
                        empty_guesses = False
                        dest_states.append(
                            self._process_guess_destination_state(
                                bel_supp, guess, guessing_cmdp, queue
                            )
                        )

                    if empty_guesses:
                        dest_states.append(
                            self._process_guess_destination_state(
                                bel_supp, None, guessing_cmdp, queue
                            )
                        )

            guessing_cmdp.add_action(
                src_state,
                uniform(dest_states),
                bel_supp_action.label,
                bel_supp_action.cons,
            )

    def _process_guess_destination_state(
        self,
        bel_supp: List[int],
        guess: Optional[int],
        guessing_cmdp: GuessingConsMDP,
        queue: deque,
    ) -> int:
        if (tuple(bel_supp), guess) not in guessing_cmdp.bel_supp_guess_indexer.keys():
            reload = self.reloads[bel_supp[0]]
            name = bel_supp_guess_state_name(bel_supp, guess)
            guessing_cmdp.new_state(bel_supp, reload, name, guess)
            queue.append((bel_supp, guess))
            return guessing_cmdp.num_states - 1
        else:
            return guessing_cmdp.bel_supp_guess_indexer[(tuple(bel_supp), guess)]
