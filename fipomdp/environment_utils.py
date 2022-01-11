import time
from typing import List, Tuple

from fipomdp import ConsPOMDP


def set_cross_observations_to_UUV_grid(cpomdp: ConsPOMDP, grid_size: [int, int]) -> None:
    """Method for setting cross sized observations to each state in the grid (one field up,left,right,down).

    3x3 grid, state at index [1][1]:

    **xxx** --> **xox**

    **xsx** --> **ooo**

    **xxx** --> **xox**

    Parameters
    ----------
    cpomdp: ConsPOMDP
        ConsPOMDP representation of the environment
    grid_size: [int, int]
        2D Grid size
    """

    obs_probs = {}
    row, col = grid_size[0], grid_size[1]

    for i in range(row):
        for j in range(col):
            central_reload = cpomdp.reloads[i*row+j]
            central_prob = 0.8
            obs = i*row + j
            tmp_obs_probs = {((i-1)*row+j, obs): 0.05,
                             ((i+1)*row+j, obs): 0.05,
                             (i*row+(j-1), obs): 0.05,
                             (i*row+(j+1), obs): 0.05}
            if i == 0 or cpomdp.reloads[(i-1)*row+j] is not central_reload: # near wall checks or
                central_prob += 0.05
                tmp_obs_probs.pop(((i-1)*row+j, obs))
            if i == grid_size[0]-1 or cpomdp.reloads[(i+1)*row+j] is not central_reload:
                central_prob += 0.05
                tmp_obs_probs.pop(((i+1)*row+j, obs))
            if j == 0 or cpomdp.reloads[i*row+(j-1)] is not central_reload:
                central_prob += 0.05
                tmp_obs_probs.pop((i*row+(j-1), obs))
            if j == grid_size[1]-1 or cpomdp.reloads[i*row+(j+1)] is not central_reload:
                central_prob += 0.05
                tmp_obs_probs.pop((i*row+(j+1), obs))
            tmp_obs_probs[(i*row+j, obs)] = round(central_prob, 2)
            obs_probs.update(tmp_obs_probs)
    cpomdp.set_observations(grid_size[0]*grid_size[1], obs_probs)


def get_guessing_stats(cpomdp: ConsPOMDP, initial_belief_support: List[int]) -> Tuple[float, int, int, int]:
    """Method for tracking time of guessing construction CMDP computation.

    Parameters
    ---------
    cpomdp: ConsPOMDP
        ConsPOMDP to be computed on
    initial_belief_support: List[int]
        Belief support for which to compute
    Returns
    -------
    Tuple[float, int, int, int]
        Duration of computation,
        Number of cpomdp states,
        Number of belief support cmdp states,
        Number of guessing cmdp states.
    """
    start = time.time()
    cpomdp.compute_guessing_cmdp_initial_state(initial_belief_support)
    return time.time() - start, cpomdp.num_states, cpomdp.belief_supp_cmdp.num_states, cpomdp.guessing_cmdp.num_states
