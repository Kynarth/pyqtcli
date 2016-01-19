import os
import click

from pyqtcli import __version__
from pyqtcli.config import ProjectConfig


@click.group()
@click.version_option(version=__version__)
def pyqtcli():
    """A command line tool to help in managing PyQt5 project."""
    pass


@pyqtcli.command("init", short_help="Initialize pyqtcli in current directory")
@click.option("-q", "-quiet", is_flag=True, help="Doesn't display any messages")
@click.option("-y", "-yes", is_flag=True, help="Send 'yes' answer to prompt")
def init(quiet, yes):
    """Initialize pyqtcli for the current PyQt5 project."""
    message = None  # Message to inform the user about the initialization

    # Verify that no other project config exist
    if os.path.isfile(ProjectConfig.NAME) and not yes:
        if click.confirm("Do you want to reset pyqtcli config?", abort=True):
            os.remove(ProjectConfig.NAME)
            message = "Pyqtcli config reset"

    # User wants to overwrite previous config file without prompt
    elif os.path.isfile(ProjectConfig.NAME) and yes:
        os.remove(ProjectConfig.NAME)
        message = "Pyqtcli config reset"

    # Generate project config file
    if not quiet:
        ProjectConfig(msg=message)
    else:
        ProjectConfig(verbose=False)


@pyqtcli.command("new", short_help="Generate a new qrc file")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("path", default="res.qrc", type=click.Path(writable=True))
@click.argument("res_folder", type=click.Path(exists=True, file_okay=False),
                nargs=1, required=False)
def new(path, res_folder, verbose):
    pass
