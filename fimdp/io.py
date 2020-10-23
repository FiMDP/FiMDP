import json

import stormpy
from .core import ConsMDP
from .explicit import product_energy


def get_state_name(model, state):
    lines = [str(state.id) + ":"]
    labeling = model.state_valuations.get_json(state)
    for k, v in json.loads(labeling).items():
        lines.append(f"{k}={v}")
    return " ".join(lines)


def storm_sparsemdp_to_consmdp(sparse_mdp,
                               state_valuations=True,
                               action_labels=True,
                               return_targets=False):
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

    :param return_targets: If True (default False), parse also target states
    (from labels).

    :return: `ConsMDP` object or
             `ConsMDP, list of targets` if `return_targets`
    """
    if "consumption" not in sparse_mdp.reward_models:
        raise ValueError("The supplied `sparse_mdp` does not have the "
                         "`consumption` reward defined")
    if "reload" not in sparse_mdp.labeling.get_labels():
        raise ValueError("The supplied `sparse_mdp` does not have the "
                         "`reload` state-label defined")
    if return_targets and "target" not in sparse_mdp.labeling.get_labels():
        raise ValueError("The supplied `sparse_mdp` does not have the "
                         "`target` state-label defined")

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
    if return_targets:
        targets = sparse_mdp.labeling.get_states("target")

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
            distr = {entry.column: entry.value() for entry in action.transitions}
            mdp.add_action(state.id, distr, a_label, int(a_cons))

    if return_targets:
        return mdp, list(targets)
    else:
        return mdp


def prism_to_consmdp(filename, constants=None, state_valuations=True,
                     action_labels=True, return_targets=False):
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

    The dict `constants` must be given if a parametric prism model is to be
    read. It must defined all unused constants of the parametric model that
    affect the model's state space. On the other hand, it must not be defined
    if the model is not parametric. The format of the dictionary is
    `{ "constant_name" : constant_value }` where constant value is either an
    integer or a string that contains a name of other constant.

    :param filename: Path to the PRISM model. Must be an mdp.

    :param constants: Dictionary for uninitialized constant initialization.
    :type: constants: dict[str(constant_names) -> int/str(constant_names)]

    :param state_valuations: If True (default), set the valuation of states as
    names in the resulting ConsMDP.
    :param action_labels: If True (default), copies the choice labels in the
    PRISM model into the ConsMDP as action labels.

    :param return_targets: If True (default False), return also the list of
    states labeled by the label `target`.

    :return: ConsMDP object for the given model, or
             `ConsMDP, targets` if `return_targets`
    """
    prism_prog = stormpy.parse_prism_program(filename)

    if constants is None:
        constants = {}
    elif not prism_prog.has_undefined_constants and len(constants) > 0:
        raise ValueError("There are no constants to be defined")

    prism_constants = {}
    man = prism_prog.expression_manager
    for const, value in constants.items():
        var = man.get_variable(const)
        if type(value) == int:
            expression = man.create_integer(value)
        elif type(value) == str:
            expression = man.get_variable(value).get_expression()
        # elif type(value) == stormpy.storage.Expression:
        #     expression = value
        else:
            raise ValueError("Constants values must be either int, "
                             "str (a name of another constant), or "
                             "a stormpy Expression.")
        prism_constants[var] = expression

    prism_prog = prism_prog.define_constants(prism_constants)

    options = stormpy.BuilderOptions()
    if state_valuations:
        options.set_build_state_valuations()
    if action_labels:
        options.set_build_choice_labels()

    model = stormpy.build_sparse_model_with_options(prism_prog, options)

    res = storm_sparsemdp_to_consmdp(model,
                                     state_valuations=state_valuations,
                                     action_labels=action_labels,
                                     return_targets=return_targets)

    return res


def parse_cap_from_prism(filename):
    prism_prog = stormpy.parse_prism_program(filename)

    for cons in prism_prog.constants:
        if cons.name == "capacity":
            return cons.definition.evaluate_as_int()

    return None


def consmdp_to_storm_consmdp(cons_mdp, targets=None):
    """
    Convert a ConsMDP object from FiMDP into a Storm's SparseMDP representation.

    The conversion works in reversible way. In particular, it does not encode
    the energy levels into state-space. Instead, it uses the encoding using
    rewards.

    The reloading and target states (if given) are encoded using state-labels
    in the similar fashion.

    :param cons_mdp: ConsMDP object to be converted
    :param targets: A list of targets (default None). If specified, each state
    in this list is labeled with the label `target`.
    :return: SparseMDP representation from Stormpy of the cons_mdp.
    """
    builder = stormpy.SparseMatrixBuilder(rows=0, columns=0, entries=0,
                                          force_dimensions=False,
                                          has_custom_row_grouping=True,
                                          row_groups=0)
    action_c = 0
    consumption = []
    action_labeling = stormpy.storage.ChoiceLabeling(len(cons_mdp.actions) - 1)

    for state in range(cons_mdp.num_states):
        # Each state has its own group
        # Each row is one action (choice)
        builder.new_row_group(action_c)

        for action in cons_mdp.actions_for_state(state):
            for dst, prob in action.distr.items():
                builder.add_next_value(action_c, dst, prob)

            consumption.append(action.cons)

            if action.label not in action_labeling.get_labels():
                action_labeling.add_label(action.label)
            action_labeling.add_label_to_choice(action.label, action_c)

            action_c += 1

    transitions = builder.build()

    # Consumption
    cons_rew = stormpy.SparseRewardModel(
        optional_state_action_reward_vector=consumption)
    rewards = {"consumption": cons_rew}

    # Reloads
    state_labeling = stormpy.storage.StateLabeling(cons_mdp.num_states)
    state_labeling.add_label("reload")
    for state in range(cons_mdp.num_states):
        if cons_mdp.is_reload(state):
            state_labeling.add_label_to_state("reload", state)

    # Targets
    if targets is not None:
        state_labeling.add_label("target")
        for state in targets:
            state_labeling.add_label_to_state("target", state)

    # Plug it all together
    components = stormpy.SparseModelComponents(
        transition_matrix=transitions,
        state_labeling=state_labeling,
        reward_models=rewards,
        rate_transitions=False)
    components.choice_labeling = action_labeling

    st_mdp = stormpy.storage.SparseMdp(components)

    return st_mdp


def encode_to_stormpy(cons_mdp, capacity, targets=None):
    """
    Convert a ConsMDP object from FiMDP into a Storm's SparseMDP representation
    that is semantically equivalent.

    Running analysis on this object should yield the same results as FiMDP. The
    energy is encoded explicitly into the state space of the resulting MDP.

    The target states (if given) are encoded using state-label "target".

    :param cons_mdp: ConsMDP object to be converted
    :param capacity: capacity
    :param targets: A list of targets (default None). If specified, each state
    in this list is labeled with the label `target`.
    :return: SparseMDP representation from Stormpy of the cons_mdp.
    """
    product, product_targets = product_energy(cons_mdp, capacity, targets)
    return consmdp_to_storm_consmdp(product, product_targets)