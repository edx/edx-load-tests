#!/usr/bin/env python
"""
Standalone script to merge an arbitrary number of settings files ordered by
priority.

This script will generate a new settings yaml file and write it to standard
output.  The files are ordered on the command line from lowest priority to
highest priority, where higher priority settings override lower priority ones.

Usage:

    util/merge-settings.py settings_1.yml settings_2.yml ... settings_N.yml > merged.yml

Keys present in settings_N.yml are guaranteed to appear in the output file
because it has the highest priority.

For the purposes of simplifying usage, non-existant files are considered
equivalent to empty files, and the script will not crash.
"""

import os
import sys
import click
import yaml


def update_subkeys(destination, overrides):
    """
    Update destination keys with overrides keys, and descend recursively when
    dicts are encountered.

    This function is like dict.update, but preserves "subkeys" in the
    destination.  This is important because some settings files use a
    hierarchical key structure for clearer organization, and dict.update would
    otherwise drop keys which do not appear to be overridden.

    Arguments:
        destination (dict):
            This object will be updated with the contents from the overrides
            argument.  It may already contain mappings, and those may or may
            not persist after this function returns.
        overrides (dict):
            New values used for overriding.
    """
    new_keys = set(overrides.keys()) - set(destination.keys())
    for k in new_keys:
        destination[k] = overrides[k]

    existing_keys = set(overrides.keys()) & set(destination.keys())  # set intersection
    for k in existing_keys:
        if type(destination[k]) == dict and type(overrides[k]) == dict:
            # Both keys are mapped to dicts, so we descend.  Assume there might
            # be subkeys we want from both.
            update_subkeys(destination[k], overrides[k])
        else:
            # "base case" of recursion
            destination[k] = overrides[k]


def merge(settings_objects):
    """
    Merge multiple settings objects.

    Arguments:
        settings_objects (list of list of dict):
            Each list element represents settings files, each sublist element
            represents each yaml document in the settings file.  The settings
            objects are given in order from lowest to highest priority.
    """
    merged_public = {}
    merged_secrets = {}
    for settings in settings_objects:
        # yaml interprets voids as "null" and returns a python Null, but we
        # really think of those as empty dicts when writing settings.
        if settings[0]:
            public = settings[0]
        else:
            public = {}
        # also, yaml document which is completely absent should be considered
        # empty dicts for the purposes of merging.
        if len(settings) == 2 and settings[1]:
            secrets = settings[1]
        else:
            secrets = {}

        update_subkeys(merged_public, public)
        update_subkeys(merged_secrets, secrets)

    return (merged_public, merged_secrets)


@click.command()
@click.argument('settings_filenames', type=click.Path(), nargs=-1)
def main(settings_filenames):
    """
    The only command, and main entry point for this script.

    Arguments:
        settings_filenames (tuple of unicode strings):
            Paths to settings files (containing one or two yaml documents)
            ordered from lowest to highest priority.
    """
    existing_settings_files = []
    for filename in settings_filenames:
        if os.path.exists(filename):
            existing_settings_files.append(open(filename, 'r'))
        else:
            sys.stderr.write('skipping non-existant file: {}\n'.format(filename))

    if len(existing_settings_files) == 1:
        # Only one filename was given on the command line, so we might as well
        # preserve any comments by copying directly to stdout
        sys.stdout.write(existing_settings_files[0].read())
    else:
        settings_objects = [ list(yaml.load_all(f)) for f in existing_settings_files ]
        for f in existing_settings_files: f.close()
        merged_public, merged_secrets = merge(settings_objects)

        # only dump the secrets yaml document if it is populated
        docs_to_dump = [ merged_public ]
        if merged_secrets:
            docs_to_dump.append(merged_secrets)

        yaml.safe_dump_all(
            docs_to_dump,
            stream=sys.stdout,
            default_flow_style=False,  # Represent objects using indented blocks
                                       # rather than inline enclosures.
            explicit_start=True,  # Begin the first document with '---', per
                                  # our usual settings file syntax.
        )


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
