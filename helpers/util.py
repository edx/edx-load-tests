"""
Generally helpful utilities for edx load testing.
"""
from random import random


def choice_with_distribution(element_ratio_pairs):
    """
    Randomly choose an element with probabilities given by ratios.

    This utility function takes a mapping of elements to ratios and chooses an
    element with probability proportional to the corresponding ratio.  The
    ratios do not need to add up to 1.0.

    Args:
        element_ratio_pairs (list): List of two-tuples containing the element
            and its ratio (int or float).  E.g. [('hello', 12), ('world', 20)]

    Returns:
        An element (the first item in one of the given tuples)

    Raises:
        ValueError: If the input list is empty.
        RuntimeError: If there is a bug in this function which causes no
            element to get chosen.
    """
    if not element_ratio_pairs:
        raise ValueError('element_ratio_pairs is empty.')
    ratios_sum = sum(pair[1] for pair in element_ratio_pairs)
    random_variable = random()  # possible values are [0.0, 1.0)
    # The element is chosen based on iteratively decreasing the random variable
    # by the normalized ratio of each element until it becomes negative.
    for elem, ratio in element_ratio_pairs:
        ratio_normalized = float(ratio) / ratios_sum
        random_variable -= ratio_normalized
        if random_variable < 0:
            return elem
    raise RuntimeError(
        "Exited element selection loop without making a selection.")
