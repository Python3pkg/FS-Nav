"""
FS-Nav commandline utility
"""


import json
import os
import pprint

import click

import fsnav
import fsnav.core
import fsnav.fg_tools


def _cb_key_val(ctx, param, value):

    """
    Click callback to turn `--opt key1=val1 --opt key2=val2` into:

        {
            'key1': 'val1',
            'key2': 'val2'
        }

    Parameters
    ----------
    ctx : click.Context
        Ignored.
    param : click.Parameter
        Ignored.
    value : tuple
        List of `key=val` strings from the commandline.

    Returns
    -------
    dict
    """

    try:
        return {p.split('=')[0]: p.split('=')[1] for p in value}
    except Exception:
        raise click.BadParameter('Invalid syntax for `key=val` pair.')


@click.group()
@click.version_option(version=fsnav.__version__)
@click.option(
    '--no-pretty', is_flag=True, help="Don't format output"
)
@click.option(
    '--configfile', type=click.Path(), default=fsnav.core.CONFIGFILE,
    help="Specify configfile"
)
@click.option(
    '--no-load-default', is_flag=True, help="Don't load default aliases"
)
@click.option(
    '--no-load-configfile', is_flag=True, help="Don't load the configfile"
)
@click.pass_context
def main(ctx, configfile, no_load_default, no_load_configfile, no_pretty):

    """
    FS Nav commandline utility.
    """

    # Store variables needed elsewhere
    ctx.obj = {
        'no_load_default': no_load_default,
        'no_load_configfile': no_load_configfile,
        'cfg_path': configfile,
        'loaded_aliases': fsnav.Aliases({}),
        'cfg_content': None,
        'no_pretty': no_pretty
    }

    # MAY NEED TO ADD A MORE VERBOSE WARNING HERE
    # Cache all the configfile content
    # Try-except handles configfiles that are completely empty
    try:
        if os.access(configfile, os.R_OK):
            with open(configfile) as f:
                ctx.obj['cfg_content'] = json.loads(f.read())
    except ValueError:
        pass

    # Load the default and configfile aliases according to the above settings
    if not no_load_default:
        for a, p in list(fsnav.core.DEFAULT_ALIASES.items()):
            ctx.obj['loaded_aliases'][a] = p
    if ctx.obj['cfg_content'] is not None and not \
            no_load_configfile and os.access(configfile, os.R_OK):
        for a, p in list(ctx.obj['cfg_content'][fsnav.core.CONFIGFILE_ALIAS_SECTION].items()):
            ctx.obj['loaded_aliases'][a] = p


@main.command()
@click.argument('alias', required=True)
@click.pass_context
def get(ctx, alias):

    """
    Print out the path assigned to an alias.
    """

    click.echo(ctx.obj['loaded_aliases'][alias])


@main.command()
@click.pass_context
def aliases(ctx):

    """
    Print recognized aliases.
    """

    aliases_ = {str(a): str(p) for a, p in list(ctx.obj['loaded_aliases'].as_dict().items())}
    if ctx.obj['no_pretty']:
        text = json.dumps(aliases_)
    else:
        text = pprint.pformat(aliases_)
    click.echo(text)


@main.group()
def startup():

    """
    Code needed to enable shortcuts on startup.
    """

    pass


@startup.command()
@click.pass_context
def generate(ctx):

    """
    Shell function shortcuts.
    """

    click.echo(' ; '.join(fsnav.fg_tools.generate_functions(ctx.obj['loaded_aliases'])))


@startup.command()
def profile():

    """
    Code to activate shortcuts on startup.
    """

    click.echo(fsnav.fg_tools.startup_code)


@main.group()
def config():

    """
    Configure FS Nav.
    """

    pass


@config.command()
@click.pass_context
def default(ctx):

    """
    Print the default aliases.
    """

    default_aliases = {
        str(a): str(p) for a, p in
        list(ctx.obj['loaded_aliases'].default().as_dict().items())}
    if ctx.obj['no_pretty']:
        text = json.dumps(default_aliases)
    else:
        text = pprint.pformat(default_aliases)
    click.echo(text)


@config.command()
@click.pass_context
def userdefined(ctx):

    """
    Print user-defined aliases.
    """

    nd_aliases = {
        str(a): str(p) for a, p in
        list(ctx.obj['loaded_aliases'].user_defined().as_dict().items())}
    if ctx.obj['no_pretty']:
        text = json.dumps(nd_aliases)
    else:
        text = pprint.pformat(nd_aliases)
    click.echo(text)


@config.command()
@click.argument(
    'alias_path', metavar='alias=path', nargs=-1, required=True, callback=_cb_key_val,
)
@click.option(
    '--no-overwrite', is_flag=True, help="Don't overwrite configfile if it exists"
)
@click.pass_context
def addalias(ctx, alias_path, no_overwrite):

    """
    Add a user defined alias.
    """

    if no_overwrite and os.access(ctx.obj['cfg_path'], os.W_OK):
        raise click.ClickException(
            "ERROR: No overwrite is {no_overwrite} and configfile exists: {configfile}".format(
                no_overwrite=no_overwrite, configfile=ctx.obj['cfg_path']))

    aliases_ = ctx.obj['loaded_aliases'].copy()
    aliases_.update(**alias_path)
    with open(ctx.obj['cfg_path'], 'w') as f:
        json.dump({fsnav.core.CONFIGFILE_ALIAS_SECTION: aliases_.user_defined()}, f)


@config.command()
@click.pass_context
def path(ctx):

    """
    Print the path to the configfile.
    """

    click.echo(ctx.obj['cfg_path'])


@config.command()
@click.argument(
    'alias', required=True, nargs=-1
)
@click.option(
    '-no', '--no-overwrite', is_flag=True,
    help="Don't overwrite configfile if it exists"
)
@click.pass_context
def deletealias(ctx, alias, no_overwrite):

    """
    Remove an alias from the configfile.
    """

    if no_overwrite and os.access(ctx.obj['cfg_path'], os.W_OK):
        raise click.ClickException(
            "ERROR: No overwrite is {no_overwrite} and configfile exists: {configfile}".format(
                no_overwrite=no_overwrite, configfile=ctx.obj['cfg_path']))

    aliases_ = fsnav.Aliases(
        {a: p for a, p in list(ctx.obj['loaded_aliases'].items()) if a not in alias})
    with open(ctx.obj['cfg_path'], 'w') as f:
        json.dump({fsnav.core.CONFIGFILE_ALIAS_SECTION: aliases_.user_defined()}, f)
