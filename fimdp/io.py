import decimal
import json

import stormpy
from .core import ConsMDP

decimal.getcontext().prec=4


def get_state_name(model, state):
    lines = [str(state.id) + ":"]
    labeling = model.state_valuations.get_json(state)
    for k, v in json.loads(labeling).items():
        lines.append(f"{k}={v}")
    return " ".join(lines)


def storm_sparsemdp_to_consmdp(sparse_mdp,
                               state_valuations=True,
                               action_labels=True):
    """
    Convert Storm's sparsemdp model to ConsMDP.

    :param sparse_mdp: Stormpy sparse representation of MDPs. The model must
    represent an MDP and it needs to contain action-based reward called
    `consumption` (needs to be defined for each action) and some states
    need to be labeled by `reload` label. In particular, `reload` must be a
    valid state label.
    :type sparse_mdp: stormpy.storage.storage.SparseMdp

    :param state_valuations: if True (default), record the state valuations
    (for models built from symbolic description) into state names of the
    ConsMDP. It is ignored if the `sparse_mdp` does not contain the state
    valuations.
    :type state_valuations: Bool

    :param action_labels: If True (default), actions are labeled by labels
    stored in `sparse_mdp.choice_labeling` (if it is present in the model).
    Otherwise, the actions are labeled by thier id.
    :type action_labels: Bool

    :return: ConsMDP object
    """
    if "consumption" not in sparse_mdp.reward_models:
        raise ValueError("The supplied `sparse_mdp` does not have the "
                         "`consumption` reward defined")
    if "reload" not in sparse_mdp.labeling.get_labels():
        raise ValueError("The supplied `sparse_mdp` does not have the "
                         "`reload` state-label defined")
    decimal.getcontext().prec = 4

    state_valuations = state_valuations and sparse_mdp.has_state_valuations()
    action_labels = action_labels and sparse_mdp.has_choice_labeling()

    cons = sparse_mdp.reward_models["consumption"]
    if action_labels:
        labels = sparse_mdp.choice_labeling

    mdp = ConsMDP()

    # Add states and detect reloads
    mdp.new_states(sparse_mdp.nr_states)
    for rel in sparse_mdp.labeling.get_states("reload"):
        mdp.set_reload(rel)

    # Add actions
    for state in sparse_mdp.states:
        if state_valuations:
            mdp.names[state.id] = get_state_name(sparse_mdp, state)
        for action in state.actions:
            a_id = sparse_mdp.get_choice_index(state.id, action.id)
            a_cons = cons.get_state_action_reward(a_id)

            # assign action label
            if action_labels:
                a_labels = labels.get_labels_of_choice(a_id)
                if len(a_labels) > 0:
                    a_label = ", ".join(list(a_labels))
                else:
                    a_label = a_id
            else:
                a_label = a_id
            distr = {entry.column: decimal.Decimal(entry.value()).normalize()
                     for entry in action.transitions}
            mdp.add_action(state.id, distr, a_label, int(a_cons))

    return mdp


def prism_to_consmdp(filename, state_valuations=True, action_labels=True):
    """
    Build a ConsMDP from a PRISM symbolic description using Stormpy.

    The model must specify `consumption` reward on each action (choice) and
    it needs to contain `reload` label.

    The following code sets the consumption of each action to `1` and marks
    each state where the variable `rel` is equal to `1` as a reloading state.

    >>> rewards "consumption"
    >>>   [] true: 1;
    >>>	endrewards
    >>> label "reload" = (rel=1);

    :param filename: Path to the PRISM model. Must be an mdp.
    :param state_valuations: If True (default), set the valuation of states as
    names in the resulting ConsMDP.
    :param action_labels: If True (default), copies the choice labels in the
    PRISM model into the ConsMDP as action labels.

    :return: ConsMDP object for the given model.
    """
    prism_prog = stormpy.parse_prism_program(filename)
    options = stormpy.BuilderOptions()
    if state_valuations:
        options.set_build_state_valuations()
    if action_labels:
        options.set_build_choice_labels()
    model = stormpy.build_sparse_model_with_options(prism_prog, options)

    return storm_sparsemdp_to_consmdp(model,
                                      state_valuations=state_valuations,
                                      action_labels=action_labels)
