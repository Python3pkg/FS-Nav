"""
FS Nav commandline interface
"""


import sys

import click

import fsnav
from fsnav.cmdl import options


# =========================================================================== #
#   Main CLI command group
# =========================================================================== #

@click.group(help="FS Nav commandline utility")
@options.version
@options.license
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument(
    'alias', required=True
)
@click.pass_context
def get(ctx, alias):

    """
    Print out the path assigned to an alias
    """

    try:
        aliases = fsnav.Aliases(**fsnav.settings.DEFAULT_ALIASES)
        click.echo(aliases[alias])
    except KeyError:
        click.echo("ERROR: Invalid alias: %s" % alias)
        sys.exit(1)

    sys.exit(0)
