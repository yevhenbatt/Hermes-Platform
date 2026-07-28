from __future__ import annotations

import argparse

from .doctor import doctor_command


def register_cli(subparser: argparse.ArgumentParser) -> None:
    """
    Build the `hermes platform` command tree.
    """

    subs = subparser.add_subparsers(
        dest="platform_command"
    )

    subs.add_parser(
        "doctor",
        help="Diagnose Hermes Platform infrastructure",
    )

    subparser.set_defaults(
        func=platform_command
    )


def platform_command(args) -> int:
    """
    Dispatch platform subcommands.
    """

    command = getattr(
        args,
        "platform_command",
        None,
    )

    if command == "doctor":
        result = doctor_command()

        if isinstance(result, int):
            return result

        if result:
            print(result)

        return 0

    print(
        "usage: hermes platform {doctor}"
    )

    return 2
