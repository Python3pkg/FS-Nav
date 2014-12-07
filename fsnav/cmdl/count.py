"""
FS Nav count utility
"""


import sys

import click

import fsnav
from fsnav.cmdl import options


@click.command()
@options.version
@options.license
@click.argument(
    'paths', metavar='path', nargs=-1, required=True
)
@click.pass_context
def main(ctx, paths):

    """
    Quickly count items on the file system.

    Only paths that exist will be counted
    """

    click.echo(fsnav.count(paths))

    sys.exit(0)
