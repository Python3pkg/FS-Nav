"""
FS Nav commandline interface
"""


import json
import os
import pprint
import sys

import click

import fsnav
from fsnav.cmdl import options


# =========================================================================== #
#   Command group: main
# =========================================================================== #

@click.group(help="FS Nav commandline utility")
@click.option(
    '-c', '--configfile', type=click.Path(), default=fsnav.settings.CONFIGFILE,
    help="Specify configfile"
)
@click.option(
    '-nld', '--no-load-default', is_flag=True,
    help="Don't load default aliases"
)
@options.version
@options.license
@click.pass_context
def main(ctx, configfile, no_load_default):

    # Store variables needed elsewhere
    ctx.obj = {
        'no_load_default': no_load_default,
        'cfg_path': configfile
    }

    # Cache the configfile content
    if os.access(configfile, os.R_OK):
        with open(configfile) as f:
            ctx.obj['cfg_content'] = json.load(f)
    else:
        ctx.obj['cfg_content'] = {}

    # Load the default and configfile aliases according to the above settings
    if no_load_default:
        ctx.obj['loaded_aliases'] = fsnav.Aliases(ctx.obj['cfg_content'])
    else:
        ctx.obj['loaded_aliases'] = fsnav.Aliases(
            fsnav.settings.DEFAULT_ALIASES.items() + ctx.obj['cfg_content'].items()
        )


# --------------------------------------------------------------------------- #
#   Command: get
# --------------------------------------------------------------------------- #

@main.command()
@click.argument(
    'alias', required=True,
)
@click.pass_context
def get(ctx, alias):

    """
    Print out the path assigned to an alias
    """

    try:
        click.echo(ctx.obj['loaded_aliases'][alias])
    except KeyError:
        click.echo("ERROR: Invalid alias: %s" % alias)
        sys.exit(1)

    sys.exit(0)


# =========================================================================== #
#   Command group: startup
# =========================================================================== #

@main.group()
@click.pass_context
def startup(ctx):

    """
    Code needed to enable shortcuts on startup
    """

    pass


# --------------------------------------------------------------------------- #
#   Command: generate
# --------------------------------------------------------------------------- #

@startup.command()
@click.pass_context
def generate(ctx):

    """
    Shell function shortcuts
    """

    try:
        click.echo(' ; '.join(fsnav.fg_tools.generate_functions(ctx.obj['loaded_aliases'])))
    except Exception as e:
        click.echo(e, err=True)

    sys.exit(0)


# --------------------------------------------------------------------------- #
#   Command: profile
# --------------------------------------------------------------------------- #

@startup.command()
@click.pass_context
def profile(ctx):

    """
    Code to activate shortcuts on startup
    """

    click.echo(fsnav.fg_tools.startup_code)
    sys.exit(0)


# =========================================================================== #
#   Command group: config
# =========================================================================== #

@main.group()
@click.pass_context
def config(ctx):

    """
    Configure FS Nav
    """

    pass

# --------------------------------------------------------------------------- #
#   Command: default
# --------------------------------------------------------------------------- #

@config.command()
@click.option(
    '-np', '--no-pretty', is_flag=True,
    help="Don't format output"
)
@click.pass_context
def default(ctx, no_pretty):
    
    """
    Print the default aliases
    """

    _d_aliases = fsnav.settings.DEFAULT_ALIASES
    d_aliases = dict((str(a), str(p)) for a, p in _d_aliases.items() if a not in ctx.obj['cfg_content'])

    if no_pretty:
        text = d_aliases
    else:
        text = pprint.pformat(d_aliases)

    click.echo(text)
    sys.exit(0)


# --------------------------------------------------------------------------- #
#   Command: nondefault
# --------------------------------------------------------------------------- #

@config.command()
@click.option(
    '-np', '--no-pretty', is_flag=True,
    help="Don't format output"
)
@click.pass_context
def nondefault(ctx, no_pretty):
    
    """
    Print the non-default aliases
    """

    try:
        nd_aliases = {}
        for alias, path in fsnav.Aliases(ctx.obj['cfg_content']).items():
            if alias not in fsnav.settings.DEFAULT_ALIASES:
                nd_aliases[alias] = path
            elif path != fsnav.settings.DEFAULT_ALIASES[alias]:
                nd_aliases[alias] = path
    except KeyError as e:
        click.echo(e, err=True)
        sys.exit(1)

    # Remove unicode 'u' in printout to allow serialization
    nd_aliases = dict((str(k), str(v)) for k, v in nd_aliases.items())

    if no_pretty:
        text = nd_aliases
    else:
        text = pprint.pformat(nd_aliases)

    click.echo(text)
    sys.exit(0)

# --------------------------------------------------------------------------- #
#   Command: set
# --------------------------------------------------------------------------- #

@config.command()
@click.argument(
    'alias_path', metavar='alias=path', nargs=-1, required=True,
)
@click.option(
    '-no', '--no-overwrite', is_flag=True,
    help="Don't overwrite configfile if it exists"
)
@click.pass_context
def set(ctx, alias_path, no_overwrite):

    """
    Add additional aliases to be stored in a configfile
    """

    if no_overwrite and os.access(ctx.obj['cfg_path'], os.W_OK):
        click.echo("ERROR: Overwrite=%s and configfile exists: %s" % (no_overwrite, ctx.obj['cfg_path']))
        sys.exit(1)

    # Validate
    for ap in alias_path:
        if '=' not in ap:
            click.echo("ERROR: Invalid syntax for new alias: %s" % ap)
            sys.exit(1)

    try:
        d_aliases = fsnav.settings.DEFAULT_ALIASES
        new_aliases = fsnav.Aliases()
        for ap in alias_path:
            alias, path = ap.split('=')
            if alias not in d_aliases or d_aliases[alias] != path:
                new_aliases[alias] = path
    except Exception as e:
        click.echo(e)
        sys.exit(1)

    with open(ctx.obj['cfg_path'], 'w') as f:
        json.dump(new_aliases.as_dict(), f)

    sys.exit(0)


# --------------------------------------------------------------------------- #
#   Command: path
# --------------------------------------------------------------------------- #

@config.command()
@click.pass_context
def path(ctx):

    """
    Print the path to the configfile
    """

    click.echo(ctx.obj['cfg_path'])
    sys.exit(0)
