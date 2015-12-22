#!/usr/bin/env python3

import os
import click

from pyqtcli import __version__
from pyqtcli.qrc import QRCFile
from pyqtcli.qrc import read_qrc
from pyqtcli.qrc import generate_qrc
from pyqtcli.qrc import fill_qresource
from pyqtcli.config import PyqtcliConfig
from pyqtcli.utils import recursive_file_search
from pyqtcli.exception import PyqtcliConfigError
from pyqtcli.makerc import process_qrc_files
from pyqtcli.makealias import write_alias


pass_config = click.make_pass_decorator(PyqtcliConfig, ensure=True)


@click.group()
@click.version_option(version=__version__)
def pyqtcli():
    """A command line tool to help in managing PyQt5 project."""
    pass


@pyqtcli.group()
def new():
    """Generate a new file."""
    pass


@new.command("qrc", short_help="Generate a new qrc file")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("path", default="res.qrc", type=click.Path(writable=True))
@click.argument("res_folder", type=click.Path(exists=True, file_okay=False),
                nargs=1, required=False)
@pass_config
def qrc(config, path, verbose, res_folder):
    """Create a new qrc file."""
    file_path, name = os.path.split(path)

    qrc = QRCFile(name, file_path)

    # Verify qrc file doesn't already exists
    if name in config.get_qrcs():
        click.secho(
            "Error: A qrc file named \'{}\' already exists".format(name),
            fg="red", bold=True, err=True
        )
        raise click.Abort()

    # Add a new section for the created qrc file
    config.cparser.add_section(name)
    config.cparser.set(name, "path", qrc.path)

    if res_folder:
        generate_qrc(qrc, res_folder, build=False)

        # Get the relative path to the folder of resources from project
        # directory to add it to the dirs variable in corresponding qrc
        # section of config file
        rel_path = os.path.relpath(res_folder, qrc.dir_path)
        config.add_dirs(name, rel_path)

    qrc.build()
    config.save()

    if verbose:
        click.secho("Qrc file \'{}\' has been created.".format(path),
                    fg="green", bold=True)


@pyqtcli.command("init", short_help="Initialize pyqtcli in current directory")
@click.option("-q", "--quiet", is_flag=True, help="No input from the command")
@click.option("-y", "--yes", is_flag=True, help="Send 'yes' anwser to prompt")
def init(quiet, yes):
    """Initialize pyqtcli for the current PyQt5 project."""
    message = None
    # Verify that another pyqtcli config file does not already exist
    if os.path.isfile(PyqtcliConfig.INI_FILE) and not yes:
        if click.confirm("Do you want to reset pyqtcli config?", abort=True):
            os.remove(PyqtcliConfig.INI_FILE)
            message = "Pyqtcli config reset"

    elif os.path.isfile(PyqtcliConfig.INI_FILE) and yes:
        os.remove(PyqtcliConfig.INI_FILE)
        message = "Pyqtcli config reset"

    # Generate project config file
    if not quiet:
        PyqtcliConfig(msg=message)
    else:
        PyqtcliConfig(verbose=False)


@pyqtcli.command("addqres", short_help="Create a <qresource> element in qrc")
@click.option("-a", "--alias", is_flag=True,
              help="Create aliases for <file> elements")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("qrc", type=click.Path(exists=True, dir_okay=False))
@click.argument("res_folders", nargs=-1,
                type=click.Path(exists=True, file_okay=False))
@pass_config
def addqres(config, qrc, res_folders, alias, verbose):
    """
    Add <qresource> element with a prefix attribute set to the base name of
    the given folder of resources. All resources contained in this folder are
    recorded in qresource as <file> subelement.
    """
    qrcfile = read_qrc(qrc)
    recorded_dirs = config.get_dirs(qrcfile.name)

    # Remove duplication in res_folders with a set
    res_folders = set(res_folders)

    # Process each resource folders passed
    for folder in res_folders:
        # rel_path => relative path of folder from project directory
        rel_path = os.path.relpath(folder, config.dir_path)

        # Check if given resources folder has already been recorded
        if rel_path in recorded_dirs:
            click.secho("Warning: You have already added \'{}\' to {}.".format(
                folder, qrcfile.name), fg="yellow", bold=True)
            continue

        # Add folder to dirs variable in the config file
        try:
            config.add_dirs(qrcfile.name, rel_path, commit=False)
        except PyqtcliConfigError:
            click.secho(
                "Error: {} isn't part of the project.".format(qrc),
                fg="yellow", bold=True
            )
            raise click.Abort()

        # Add qresource to qrc file
        prefix = "/" + os.path.basename(folder)
        qrcfile.add_qresource(prefix)
        fill_qresource(qrcfile, folder, prefix)

        if verbose:
            click.secho(
                "qresource with prefix: \'{}\' has been recorded in {}.".format(
                    "/" + os.path.basename(folder), qrc), fg="green", bold=True)

    qrcfile.build()
    config.save()

    if alias:
        write_alias([qrcfile.path], verbose)


@pyqtcli.command("rmqres", short_help="Remove a <qresource> element in qrc")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("qrc", type=click.Path(exists=True, dir_okay=False))
@click.argument("res_folders", nargs=-1,
                type=click.Path(exists=True, file_okay=False))
@pass_config
def rmqres(config, qrc, res_folders, verbose):
    """
    Remove a <qresource> element with a prefix attribute set to the base name
    of the given folder of resources. All <file> subelements are removed too.
    """
    qrcfile = read_qrc(qrc)

    # Remove duplication in res_folders with a set
    res_folders = set(res_folders)

    folders = [os.path.relpath(f, config.dir_path) for f in res_folders]

    # remove folder to dirs variable in the config file
    try:
        config.rm_dirs(qrcfile.name, folders, commit=False)
    except PyqtcliConfigError:
        click.secho(
            "Error: {} isn't part of the project.".format(qrc),
            fg="yellow", bold=True
        )
        raise click.Abort()

    for folder in folders:
        # Remove qresource to qrc file
        prefix = "/" + os.path.basename(folder)
        qrcfile.remove_qresource(prefix)

        if verbose:
            click.secho(
                "Resources folder: \'{}\' has been removed in {}.".format(
                    folder, qrc), fg="green", bold=True)

    config.save()
    qrcfile.build()


@pyqtcli.command("makealias", short_help="Add aliases to qrc's resources")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process")
@click.argument('qrc_files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def makealias(qrc_files, recursive, verbose):
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_file_search("qrc")

        # Check if recursive option find qrc files
        if recursive_qrc_files == []:
            click.secho(
                "Error: Could not find any qrc files.",
                err=True, fg="red", bold=True)
            raise click.Abort()
        else:
            write_alias(recursive_qrc_files, verbose)

    # Process given files or warns user if none
    if qrc_files:
        write_alias(qrc_files, verbose)
    elif not recursive:
        click.secho("Warning: No qrc files was given to process.",
                    fg="yellow", bold=True)


@pyqtcli.command("makerc", short_help="Generate python qrc module to given qrc")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process.")
@click.argument('qrc_files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def makerc(qrc_files, recursive, verbose):
    """Generate python module for corresponding given qrc files."""
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_file_search("qrc")

        # Check if recursive option find qrc files
        if recursive_qrc_files == []:
            click.secho(
                "Error: Could not find any qrc files",
                err=True, fg="red", bold=True)
        else:
            process_qrc_files(recursive_qrc_files, verbose)

    # Process given files or warns user if none
    if qrc_files:
        process_qrc_files(qrc_files, verbose)
    elif not recursive:
        click.secho("Warning: No qrc files was given to process.",
                    fg="yellow", bold=True)
