#!/usr/bin/env python3

import os
import click
import subprocess


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1.0')
def pyqtcli():
    """A command line tool to help in managing PyQt5 project."""
    pass


@pyqtcli.command("makerc", short_help="Generate python qrc module")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument('qrc_files', nargs=-1, type=click.Path(exists=True))
def makerc(qrc_files, verbose):
    """Generate python module for corresponding given qrc files."""
    if qrc_files == ():
        click.secho("Warning: No qrc files was given to process.", fg="yellow")

    # Process each given qrc files
    for qrc_file in qrc_files:
        # Get absolute path
        qrc_file = os.path.abspath(qrc_file)

        result_file = os.path.splitext(qrc_file)[0] + "_rc.py"
        # if not subprocess.call(["pyrcc5", qrc_file, "-o", result_file]):
        if subprocess.call(["pyrcc5", qrc_file, "-o", result_file]):
            # Let pyrcc5 give his error message
            continue

        # Manage -v --verbose option
        if verbose:
            click.echo("Python qrc file '{}' created.".format(result_file))


if __name__ == "__main__":
    pyqtcli()
