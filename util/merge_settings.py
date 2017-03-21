"""
Merge an arbitrary number of settings files ordered by priority.

This script will generate a new settings yaml file and write it to standard
output.  The files are ordered on the command line from lowest priority to
highest priority, where higher priority settings override lower priority ones.

Usage:

    pip install -e .  # from the root of edx-load-tests
    merge_settings settings_1.yml settings_2.yml ... settings_N.yml > merged.yml

Keys present in settings_N.yml are guaranteed to appear in the output file
because it has the highest priority.
"""

import sys
import click
from helpers.settings import Settings


@click.command()
@click.argument('settings_files', type=click.File(), nargs=-1)
def main(settings_files):
    """
    The only command, and main entry point for this script.

    Arguments:
        settings_files (tuple of file objects):
            The file objects refer to settings files.  The files (tuple
            elements) are ordered from lowest to highest priority.
    """
    if len(settings_files) == 1:
        # Only one filename was given on the command line, so we might as well
        # preserve any comments by copying directly to stdout
        sys.stdout.write(settings_files[0].read())
    else:
        merged_settings = Settings()
        for settings_file in settings_files:
            merged_settings.update(Settings.from_file(settings_file))
        merged_settings.dump(sys.stdout)
