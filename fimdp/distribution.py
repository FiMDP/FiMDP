"""
Module that defines probability distributions and distributions-related
functions.

A distribution is a mapping from states (integers) to probability values where
the values sum up to 1.
"""
import decimal
from decimal import Decimal

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
    return sum(probabilities) == 1


def uniform(destinations):
    """
    Create a uniform distribution for given destinations.

    destinations: iterable of states
    """
    count = len(destinations)
    mod = 100 % count
    decimal.getcontext().prec = 2
    prob = Decimal(1)/Decimal(count)
    dist = {i: prob for i in destinations}
    last = destinations[-1]
    dist[last] = dist[last] + Decimal("0.01")*mod
    return dist
