import re
from copy import copy
from typing import Tuple, List

from fimdp.core import ActionData, ConsMDP
from fimdpenv.AEVEnv import AEVEnv
from fipomdp import ConsPOMDP


class NYCPOMDPEnvironment:

    cmdp_env: AEVEnv

    def __init__(self):
        reloads = ['42431659', '42430367', '1061531810', '42443056', '1061531448', '42448735', '596775930', '42435275',
                   '42429690', '42446036', '42442528', '42440966', '42431186', '42438503', '42442977',
                   '42440966', '1061531802', '42455666']
        targets = ['42440465', '42445916']

        self.cmdp_env = AEVEnv(capacity=1000, targets=targets, reloads=reloads, init_state='42459137')
        self.cmdp_env.reset(init_state='42459137', init_energy=1000)

    def get_cpomdp(self) -> Tuple[ConsPOMDP, List[int]]:

        mdp, targets = self.cmdp_env.get_consmdp()

        original_num_states = mdp.num_states

        # States

        for state in range(original_num_states):
            mdp.new_state(mdp.reloads[state], mdp.names[state]+"_low")

        for state in range(original_num_states):
            mdp.new_state(mdp.reloads[state], mdp.names[state]+"_high")

        for state in range(original_num_states):
            actions = mdp.actions_for_state(state)
            for action in actions:
                orig_distr = {k: float(v) for k, v in action.distr.items()}
                action.distr = orig_distr  # AEVEnv uses decimal not float values, fix
                for i in range(1, 3):
                    index_shift = i*original_num_states
                    src = action.src+index_shift
                    shifted_distr = {k+index_shift: v for k, v in orig_distr.items()}
                    mdp.add_action(src, shifted_distr, action.label, action.cons)

        for state in range(original_num_states):
            if re.search("^\d+$", mdp.names[state]):  # regex matching exactly number names
                actions = mdp.actions_for_state(state)  # mid, low, high traffic state changes - actions
                for act in actions:
                    self._modify_stochastic_action(mdp, act, original_num_states)

            if re.search("^ps\d+_\d+_act\d+$", mdp.names[state]):  # regex matching exactly number + '_act' + number
                actions = mdp.actions_for_state(state)
                for act in actions:
                    self._modify_dummy_action(mdp, act, original_num_states)

        state_obs_probs = {}

        for obs in range(original_num_states):
            state_obs_probs[(obs, obs)] = 1  # mid state
            state_obs_probs[(obs+original_num_states, obs)] = 1  # low state
            state_obs_probs[(obs+2*original_num_states, obs)] = 1  # high state

        mdp.__class__ = ConsPOMDP

        observations = {}

        for i in range(3):
            for state in range(original_num_states):
                observations[(state + i*original_num_states, state)] = 1

        mdp.set_observations(original_num_states, observations)

        return mdp, targets

    def _modify_dummy_action(self, mdp: ConsMDP, mid_action: ActionData, shift: int):
        orig_distr = mid_action.distr

        if len(orig_distr.keys()) != 1:
            raise AttributeError("Given action is not one to one.")

        dest = list(orig_distr.keys())[0]
        new_distr = {dest: 0.5, dest+shift: 0.25, dest+2*shift: 0.25}
        mid_action.distr = new_distr

        low_src = mid_action.src + shift
        high_src = mid_action.src + 2*shift
        low_label = mid_action.label  # + "_low"
        high_label = mid_action.label  # + "_high"

        low_action = [act for act in mdp.actions_for_state(low_src) if act.label == low_label][0]
        high_action = [act for act in mdp.actions_for_state(high_src) if act.label == high_label][0]

        low_action_distr = {dest: 0.75, dest+shift: 0.25}
        high_action_distr = {dest: 0.75, dest+2*shift: 0.25}

        low_action.distr = low_action_distr
        high_action.distr = high_action_distr

    def _modify_stochastic_action(self, mdp: ConsMDP, mid_action: ActionData, shift: int):
        orig_distr = mid_action.distr

        action_number = mid_action.label[-1]

        if len(orig_distr.keys()) != 3:
            raise AttributeError("Given action is not one to three, three stochastic cost states required.")

        dest_states = list(orig_distr.keys())
        dest_names = [mdp.names[s] for s in dest_states]

        if not all(map(lambda name: re.search('^ps\d_\d+_act\d+$', name) is not None, dest_names)):
            raise AttributeError(f"Incorrect destination states, expected names in starting with ps: 'ps.....' got, {dest_names}.")

        low_src = mid_action.src + shift
        high_src = mid_action.src + 2*shift
        low_label = mid_action.label  # + "_low"
        high_label = mid_action.label  # + "_high"

        low_action = [act for act in mdp.actions_for_state(low_src) if act.label == low_label][0]
        high_action = [act for act in mdp.actions_for_state(high_src) if act.label == high_label][0]

        ps1_state_index = dest_names.index([name for name in dest_names if re.search(f'^ps1_\d+_act{action_number}$', name)][0])
        ps3_state_index = dest_names.index([name for name in dest_names if re.search(f'^ps3_\d+_act{action_number}$', name)][0])

        ps1_state = dest_states[ps1_state_index]
        ps3_state = dest_states[ps3_state_index]

        low_dist = copy(low_action.distr)
        low_dist[ps3_state + shift] += low_dist[ps1_state + shift]
        low_dist.pop(ps1_state + shift)

        high_dist = copy(high_action.distr)
        high_dist[ps1_state + 2*shift] += high_dist[ps3_state + 2*shift]
        high_dist.pop(ps3_state + 2*shift)

        if len(low_dist) != 2 or len(high_dist) != 2:
            raise IndexError(f"Incorrect indexing.")

        low_action.distr = low_dist
        high_action.distr = high_dist
