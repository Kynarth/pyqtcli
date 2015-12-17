#!/usr/bin/env python3

import os
import click

from pyqtcli import __version__
from pyqtcli.qrc import QRCFile
from pyqtcli.qrc import read_qrc
from pyqtcli.qrc import fill_qresource
from pyqtcli.config import PyqtcliConfig
from pyqtcli.utils import recursive_file_search
from pyqtcli.makealias import write_alias


pass_config = click.make_pass_decorator(PyqtcliConfig, ensure=True)


@click.group()
@click.version_option(version=__version__)
def pyqtcli():
    """A command line tool to help in managing PyQt5 project."""
    pass


@pyqtcli.command("init", short_help="Initialize pyqtcli in current directory")
@click.option("-q", "--quiet", is_flag=True, help="No input from the command")
@click.option("-y", "--yes", is_flag=True, help="Send 'yes' anwser to prompt")
def init(quiet, yes):
    """Initialize pyqtcli for the current PyQt5 project."""

    # Verify that another pyqtcli config file does not already exist
    if os.path.isfile(PyqtcliConfig.INI_FILE) and not yes:
        if click.confirm("Do you want to reset pyqtcli config?", abort=True):
            message = "Pyqtcli config reset"

    elif os.path.isfile(PyqtcliConfig.INI_FILE) and yes:
        message = "Pyqtcli config reset"

    else:
        message = "Pyqtcli initialized in {}".format(os.getcwd())

    # Generate project config file
    PyqtcliConfig()

    if not quiet:
        click.secho(message, fg="green", bold=True)


@pyqtcli.command("new", short_help="Generate a new file like qrc file")
@click.option("--qrc", "file_type", flag_value="qrc", default=True)
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("path", default="res.qrc", type=click.Path())
@pass_config
def new(config, file_type, path, verbose):
    """Create a new file of given type (qrc by default)."""
    file_path, name = os.path.split(path)

    if file_type == "qrc":
        qrc = QRCFile(name, file_path)
        qrc.build()

        # Verify qrc file doesn't already exists
        if name in config.get_qrcs():
            click.secho(
                "A qrc file named \'{}\' already exists".format(name),
                fg="red", bold=True
            )
            raise click.Abort()

        # Add a new section for the created qrc file
        config.cparser.add_section(name)
        config.cparser.set(name, "path", qrc.path)
        config.save()

        if verbose:
            click.secho("Qrc file \'{}\' has been created.".format(path))


@pyqtcli.command("addqres", short_help="Create a <qresource> element in qrc.")
@click.option("-a", "--alias", is_flag=True,
              help="Create aliases for <file> elements.")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("qrc", type=click.Path(exists=True, dir_okay=False))
@click.argument("res_folder", type=click.Path(exists=True, file_okay=False))
@pass_config
def addqres(config, qrc, res_folder, alias, verbose):
    """
    Add <qresource> element with a prefix attribute set to the base name of
    the given folder of resources. All resources contained in this folder are
    recorded in qresource as <file> subelement.
    """
    qrc_name = os.path.basename(qrc)

    # rel_path => relative path of res_folder from qrc file
    rel_path = os.path.relpath(res_folder, os.path.dirname(qrc))

    # Check if the given qrc file is recorded in project config file
    qrcs = config.get_qrcs()
    if qrc_name not in qrcs:
        click.secho(
            "Qrc: {} isn't part of the project.".format(qrc),
            fg="yellow", bold=True
        )
        raise click.Abort()

    # Check if given res_folder has already been recorded
    if rel_path in config.get_dirs(qrc_name):
        click.secho(
            "You have already added this resources folder to {}.".format(
                qrc_name),
            fg="yellow", bold=True
        )
        raise click.Abort()

    # Add res_folder to dirs variable in the config file
    if not config.add_dir(qrc_name, rel_path, commit=False):
        click.secho("An error occured while adding {} to config file.".format(
            res_folder))
        raise click.Abort()

    # Add qresource to qrc file
    qrcfile = read_qrc(qrc)
    qrcfile.add_qresource("/" + os.path.basename(res_folder))
    fill_qresource(qrcfile, res_folder)
    qrcfile.build()

    if alias:
        write_alias([qrcfile.path], verbose)

    config.save()

    if verbose:
        click.secho(
            "Folder: \'{}\' has been recorded in {}.".format(res_folder, qrc)
        )


@pyqtcli.command("makealias", short_help="Add aliases to qrc's resources")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process.")
@click.argument('qrc_files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def makealias(qrc_files, recursive, verbose):
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_file_search("qrc")

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
