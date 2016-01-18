import click

from pyqtcli import __version__


@click.group()
@click.version_option(version=__version__)
def pyqtcli():
    """A command line tool to help in managing PyQt5 project."""
    pass


@pyqtcli.command("new", short_help="Generate a new qrc file")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("path", default="res.qrc", type=click.Path(writable=True))
@click.argument("res_folder", type=click.Path(exists=True, file_okay=False),
                nargs=1, required=False)
def new(path, res_folder, verbose):
    pass
