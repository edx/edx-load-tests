"""Test functions in helpers.util"""

import pytest
from helpers.util import choice_with_distribution


def test_choice_with_distribution():
    """
    Make sure that choice_with_distributions basically doesn't crash, and has
    the correct type of return value.  However, do not test the distribution of
    return values unless we are certain of the value.

    The goal with this test is to NOT allow randomness to influence the result.
    """
    assert isinstance(choice_with_distribution([('a', 1), ('b', 2), ('c', 3)]), type('d'))
    assert choice_with_distribution([('a', 1), ('b', 2), ('c', 3)]) in ['a', 'b', 'c']
    assert choice_with_distribution([('a', 0), ('b', 0), ('c', 1)]) == 'c'
    assert choice_with_distribution([('a', 0), ('b', 0), ('c', 0.5)]) == 'c'
    assert choice_with_distribution([('a', 1)]) == 'a'
    assert choice_with_distribution([('a', 0.5)]) == 'a'
    with pytest.raises(ValueError):
        choice_with_distribution([])
