"""
Module that defines probability distributions and distributions-related
functions.

A distribution is a mapping from states (integers) to probability values where
the values sum up to 1.
"""
from math import floor


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


def uniform(destinations, distr_weight=100):
    """
    Create a uniform distribution for given destinations.

    destinations: iterable of states
    """
    count = len(destinations)
    prob = floor(10000/count) / 10000
    rest = 1.0 - count*prob
    dist = {i: prob for i in destinations}
    last = destinations[-1]
    dist[last] = prob+rest
    return dist
