#!/usr/bin/env python3

import click

from pyqtcli.makerc import process_qrc_files
from pyqtcli.option import recursive_process
from pyqtcli.makealias import write_alias


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.3.1')
def pyqtcli():
    """A command line tool to help in managing PyQt5 project."""
    pass


@pyqtcli.command("makerc", short_help="Generate python qrc module")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process.")
@click.argument('qrc_files', nargs=-1, type=click.Path(exists=True))
def makerc(qrc_files, recursive, verbose):
    """Generate python module for corresponding given qrc files."""
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_process()

        # Check if recursive option find qrc files
        if recursive_qrc_files == ():
            click.secho(
                "Error: Could not find any qrc files", err=True, fg="red")
        else:
            process_qrc_files(recursive_qrc_files, verbose)

    # Process given files or warns user if none
    if qrc_files:
        process_qrc_files(qrc_files, verbose)
    elif not recursive:
        click.secho("Warning: No qrc files was given to process.", fg="yellow")


@pyqtcli.command("makealias",
                 short_help="Add alias to resources within qrc files")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process.")
@click.argument('qrc_files', nargs=-1, type=click.Path(exists=True))
def makealias(qrc_files, recursive, verbose):
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_process()

        # Check if recursive option find qrc files
        if recursive_qrc_files == ():
            click.secho(
                "Error: Could not find any qrc files", err=True, fg="red")
        else:
            write_alias(recursive_qrc_files, verbose)

    # Process given files or warns user if none
    if qrc_files:
        write_alias(qrc_files, verbose)
    elif not recursive:
        click.secho("Warning: No qrc files was given to process.", fg="yellow")
