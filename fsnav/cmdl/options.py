"""
Options and flags needed by multiple commandline utilities
"""


import click

from fsnav import settings


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(settings.__version__)
    ctx.exit()


def print_license(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(settings.__license__)
    ctx.exit()


version = click.option(
    '--version', is_flag=True, callback=print_version,
    expose_value=False, is_eager=True,
    help="Print version"
)


license = click.option(
    '--license', is_flag=True, callback=print_version,
    expose_value=False, is_eager=True,
    help="Print license"
)
