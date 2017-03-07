"""Test functions in helpers.util"""

import pytest
from util.merge_settings import update_subkeys, merge

def _cmp_hierarchical_dicts(d1, d2):
    if type(d1) != dict or type(d2) != dict:
        pytest.fail("Dict keys do not match.")
    if set(d1.keys()) != set(d2.keys()):
        pytest.fail("Dict keys do not match.")
    keys_mapped_to_dicts = { k for k in d1.keys() if type(d1[k]) == dict }
    for k in keys_mapped_to_dicts:
        _cmp_hierarchical_dicts(d1[k], d2[k])
    keys_leafs = set(d1.keys()) - keys_mapped_to_dicts
    for k in keys_leafs:
        # This is our base case.  All the rest of the keys should be "leaf"
        # keys.
        if type(d1[k]) == list:
            # Lists are a special case because they're not hashable in python.
            # Assume all the elements are hashable.
            if tuple(d1[k]) != tuple(d2[k]):
                pytest.fail("Dict contents do not match.")
        else:
            # The rest of these should be strings, bools, or numbers, all of
            # which are hashable.
            if d1[k] != d2[k]:
                pytest.fail("Dict contents do not match.")

def test_update_subkeys_1():
    """
    """
    destination = {
        'hello': 1,
        'world': 2,
        'more_info': {
            'foo': 3,
            'bar': 4,
        },
        'static_info': {
            'biz': 5,
            'baz': 6,
        },
        'new_info_1': 7
    }
    overrides = {
        'hello': 10,
        'new_hello': 80,
        'more_info': {
            'foo': 30,
            'bin': 90,
            'bak': {
                'sdf': 100,
            },
        },
        'new_info_1': {
            'vnf': 110,
        },
        'new_info_2': {
            'bzb': 120,
        },
    }
    expected_destination = {
        'hello': 10,
        'new_hello': 80,
        'world': 2,
        'more_info': {
            'foo': 30,
            'bin': 90,
            'bar': 4,
            'bak': {
                'sdf': 100,
            },
        },
        'static_info': {
            'biz': 5,
            'baz': 6,
        },
        'new_info_1': {
            'vnf': 110,
        },
        'new_info_2': {
            'bzb': 120,
        },
    }
    update_subkeys(destination, overrides)
    _cmp_hierarchical_dicts(destination, expected_destination)


def test_update_subkeys_1():
    """
    """
    destination = {
        'string_not_overridden': 'original_string',
        'string_overridden_with_string': 'original_string',
        'string_overridden_with_number': 'original_string',
        'string_overridden_with_bool': 'original_string',
        'string_overridden_with_list': 'original_string',
        'string_overridden_with_dict': 'original_string',

        'number_not_overridden': 10,
        'number_overridden_with_string': 10,
        'number_overridden_with_number': 10,
        'number_overridden_with_bool': 10,
        'number_overridden_with_list': 10,
        'number_overridden_with_dict': 10,

        'list_not_overridden': [1, 2, 3],
        'list_overridden_with_string': [1, 2, 3],
        'list_overridden_with_number': [1, 2, 3],
        'list_overridden_with_bool': [1, 2, 3],
        'list_overridden_with_list': [1, 2, 3],
        'list_overridden_with_dict': [1, 2, 3],

        'dict_not_modified_or_overridden': {
            'subkey_original': 10,
        },
        'dict_overridden_with_string': {
            'subkey_irrelevant': 10,
        },
        'dict_overridden_with_number': {
            'subkey_irrelevant': 10,
        },
        'dict_overridden_with_bool': {
            'subkey_irrelevant': 10,
        },
        'dict_overridden_with_list': {
            'subkey_irrelevant': 10,
        },
        'dict_modified': {
            'subkey_unchanged': 10,
            'subkey_changed': 10,
        },
    }
    overrides = {
        # TODO
    }
    expected_destination = {
        # TODO
    }
    update_subkeys(destination, overrides)
    _cmp_hierarchical_dicts(destination, expected_destination)


def test_merge():
    """
    """
    merge([[{}], [{}]])
