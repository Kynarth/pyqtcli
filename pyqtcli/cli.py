#!/usr/bin/env python3

import os
import click

from pyqtcli import __version__
from pyqtcli.qrc import QRCFile
from pyqtcli.config import PyqtcliConfig


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

    PyqtcliConfig()

    if not quiet:
        click.secho(message, fg="green", bold=True)


@pyqtcli.command("new", short_help="Generate a new file like qrc file")
@click.option("--qrc", "file_type", flag_value="qrc", default=True)
@click.argument("path", default="res.qrc", type=click.Path())
def new(file_type, path):
    """Create a new file of given type (qrc by default)."""
    path, name = os.path.split(path)

    if file_type == "qrc":
        QRCFile(name, path).build()
