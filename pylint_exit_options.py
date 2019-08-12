#!/usr/local/bin/python3
"""
The goal of this script to add a level of customizability to exit handling for pylint
"""
from __future__ import print_function

import argparse
import sys

from bitarray import bitarray

# Package information
VERSION = __version__ = "0.1.1rc1"
__title__ = "pylint_exit_options"
__summary__ = "Exit code handler for pylint command line utility."
__uri__ = "https://github.com/lowellfarrell/pylint-exit-options"

EXIT_CODE_DFAULTS = [
    (1, 'fatal message issued', 1),
    (2, 'error message issued', 2),
    (4, 'warning message issued', 4),
    (8, 'refactor message issued', 0),
    (16, 'convention message issued', 0),
    (32, 'usage error', 32)
]


def decode(value):
    """
    Decode the return code value into a bit array.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        list of raised exit codes.

    Example:
        >>> decode(1)
        [(1, 'fatal message issued', 1)]
        >>> decode(2)
        [(2, 'error message issued', 0)]
        >>> decode(3)
        [(1, 'fatal message issued', 1), (2, 'error message issued', 0)]
    """
    return [x[1] for x in zip(bitarray(bin(value)[2:])[::-1], EXIT_CODE_DFAULTS) if x[0]]


def get_messages(value):
    """
    Return a list of raised messages for a given pylint return code.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        list of str: Raised messages.

    Example:
        >>> get_messages(1)
        ['fatal message issued']
        >>> get_messages(2)
        ['error message issued']
        >>> get_messages(3)
        ['fatal message issued', 'error message issued']
    """
    return [x[1] for x in decode(value)]


def get_exit_code(value):
    """
    Return the exist code that should be returned.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        int: Return code that should be returned when run as a command.

    Example:
        >>> get_exit_code(1)
        1
        >>> get_exit_code(2)
        2
        >>> get_exit_code(3)
        3
        >>> get_exit_code(12)
        4
    """
    exit_codes = [x[2] for x in decode(value)]
    if not exit_codes:
        return 0
    return sum(exit_codes)


def show_workings(value):
    """
    Display workings

    Args:
        value(int): Return code from pylint command line.

    Example:
        >>> show_workings(1)
        1 (1) = ['fatal message issued']
        >>> show_workings(12)
        12 (1100) = ['warning message issued', 'refactor message issued']
    """
    print("%s (%s) = %s" %
          (value, bin(value)[2:], [x[1][1] for x in zip(bitarray(bin(value)[2:])[::-1], EXIT_CODE_DFAULTS) if x[0]]))


def handle_exit_code(value):
    """
    Exit code handler.

    Takes a pylint exist code as the input parameter, and
    displays all the relevant console messages.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        int: Return code that should be returned when run as a command.

    Example:
        >>> handle_exit_code(1)
        The following messages were raised:
        <BLANKLINE>
          - fatal message issued
        <BLANKLINE>
        Fatal messages detected.  Failing...
        1
        >>> handle_exit_code(12)
        The following messages were raised:
        <BLANKLINE>
          - warning message issued
          - refactor message issued
        <BLANKLINE>
        No fatal messages detected.  Exiting gracefully...
        0
    """
    messages = get_messages(value)
    exit_code = get_exit_code(value)

    if messages:
        print('The following types of issues were found:')
        print('')

        for message in messages:
            print("  - %s" % message)

        print('')

    if exit_code:
        print('The following types of issues are blocker:')
        print('')

        exit_messages = get_messages(exit_code)
        for exit_message in exit_messages:
            print("  - %s" % exit_message)

        print('')
        print('Exiting with issues...')
    else:
        print('Exiting gracefully...')

    return exit_code


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument('pylint_exit_code', metavar='PYLINTRC', type=int,
                        help='pylint return code')

    parser.add_argument('-efail', '--error-fail', action='store_true',
                        help='Fail on issued error messages')

    parser.add_argument('-wfail', '--warn-fail', action='store_true',
                        help='fail on issued warnings messages')

    parser.add_argument('-rfail', '--refactor-fail', action='store_true',
                        help='fail on issued refactor messages')

    parser.add_argument('-cfail', '--convention-fail', action='store_true',
                        help='fail on issued convention messages')

    return parser.parse_args()


def apply_enforcement_setting(key, value):
    """
    Apply an enforcement setting

    Args:
        key (str): specific message level to set
        value (int): new value for level

    """
    positions = {
        "fatal": 0,
        "error": 1,
        "warning": 2,
        "refactor": 3,
        "convention": 4,
        "usage": 5
    }
    # fetch the position from the dict
    position = positions[key]

    # unpack the tuple so it can be modified
    encoded, description, enforce = EXIT_CODE_DFAULTS[position]
    enforce = value  # set the element to True (error)

    # repack it back into a tuple to match existing data type
    EXIT_CODE_DFAULTS[position] = encoded, description, enforce


def handle_cli_flags(namespace):
    """
    Applies the CLI flags

    Args:
        namespace (argparse.Namespace): namespace from CLI arguments

    """
    if namespace.error_fail:  # fail on errors
        apply_enforcement_setting("error", 1)

    if namespace.warn_fail:
        apply_enforcement_setting("warning", 1)

    if namespace.refactor_fail:
        apply_enforcement_setting("refactor", 1)

    if namespace.convention_fail:
        # error on conventions
        apply_enforcement_setting("convention", 1)


def main():
    """ main function """
    args = parse_args()
    handle_cli_flags(args)
    exit_code = handle_exit_code(args.pylint_exit_code)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()