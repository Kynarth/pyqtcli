#!/usr/bin/env python3

import os
import click

from pyqtcli import __version__
from pyqtcli.qrc import QRCFile
from pyqtcli.qrc import read_qrc
from pyqtcli.qrc import fill_qresource
from pyqtcli.config import PyqtcliConfig


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

    PyqtcliConfig()

    if not quiet:
        click.secho(message, fg="green", bold=True)


@pyqtcli.command("new", short_help="Generate a new file like qrc file")
@click.option("--qrc", "file_type", flag_value="qrc", default=True)
@click.argument("path", default="res.qrc", type=click.Path())
@pass_config
def new(config, file_type, path):
    """Create a new file of given type (qrc by default)."""
    path, name = os.path.split(path)

    if file_type == "qrc":
        qrc = QRCFile(name, path)
        qrc.build()

        # Add a new section for the created qrc file
        qrc_name = os.path.splitext(qrc.name)[0]
        config.cparser.add_section(qrc_name)
        config.cparser.set(qrc_name, "path", qrc.path)
        config.save()


@pyqtcli.command("addqres", short_help="Create a <qresource> element in qrc.")
@click.argument("qrc", type=click.Path(exists=True, dir_okay=False))
@click.argument("res_folder", type=click.Path(exists=True, file_okay=False))
@pass_config
def addqres(config, qrc, res_folder):
    qrc_name = os.path.splitext(qrc)[0]

    # Check if the given qrc file is recorded in project config file
    qrcs = config.get_qrcs()
    if qrc_name not in qrcs:
        click.secho("Qrc: {} isn't part of the project.".format(qrc))
        raise click.Abort()

    qrcfile = read_qrc(qrc)
    qrcfile.add_qresource("/" + os.path.basename(res_folder))
    fill_qresource(qrcfile, res_folder)
    qrcfile.build()
