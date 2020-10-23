"""
Module that defines probability distributions and distributions-related
functions.

A distribution is a mapping from states (integers) to probability values where
the values sum up to 1.
"""

def is_distribution(distribution):
    """
    Checks if the given mapping is a probability distribution (sums up to 1).

    Parameters
    ==========
    distribution: a mapping from integers to probabilities

    Returns
    =======
    True if values in `distribution` sum up to 1.

    """
    probabilities = distribution.values()
    return round(sum(probabilities), 8) == 1


def uniform(destinations):
    """
    Create a uniform distribution for given destinations.

    destinations: iterable of states
    """
    count = len(destinations)
    mod = 100 % count
    prob = 1/count
    dist = {i: prob for i in destinations}
    last = destinations[-1]
    dist[last] = dist[last] + 0.01*mod
    return dist
