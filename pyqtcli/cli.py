"""Little command line interface to manage PyQt5 projects."""

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
from pyqtcli.makealias import write_alias
from pyqtcli.update import update_project
from pyqtcli.makerc import generate_rc
from pyqtcli.qrc import get_prefix
from pyqtcli import verbose as v

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
def qrc(config, path, res_folder, verbose):
    """Create a new qrc file.

    Args:
        config (:class:`PyqtcliConfig`): PyqtcliConfig object representing
            project config file.
        path (str): Path where create the new qrc file.
        res_folder (str): Path to the folder of resources .
        verbose (bool): Boolean determining if messages will be displayed.

    """
    file_path, name = os.path.split(path)

    qrc_file = QRCFile(name, file_path)

    # Verify qrc file doesn't already exists
    if name in config.get_qrcs():
        v.error("A qrc file named \'{}\' already exists".format(name))
        raise click.Abort()

    # Add a new section for the created qrc file
    config.cparser.add_section(name)
    config.cparser.set(name, "path", qrc_file.path)

    if res_folder:
        generate_qrc(qrc_file, res_folder, build=False)

        # Get the relative path to the folder of resources from project
        # directory to add its sub dirs to the dirs variable in the
        # corresponding qrc section of config file
        rel_path = os.path.relpath(res_folder, config.dir_path)
        resources = os.listdir(rel_path)

        # If there is resources that are not in folder add the res_folder in the
        # dirs key of the config file.
        config.add_dirs(name, rel_path, commit=False)

        for d in resources:
            if os.path.isdir(os.path.join(rel_path, d)):
                config.add_dirs(name, os.path.join(rel_path, d), commit=False)

    qrc_file.build()
    config.save()

    v.info("Qrc file \'{}\' has been created.".format(path), verbose)


@pyqtcli.command("init", short_help="Initialize pyqtcli in current directory")
@click.option("-q", "--quiet", is_flag=True, help="No input from the command")
@click.option("-y", "--yes", is_flag=True, help="Send 'yes' answer to prompt")
def init(quiet, yes):
    """Initialize pyqtcli for the current PyQt5 project.

    Args:
        quiet (bool): If True, no message will be displayed.
        yes (bool): When a question is asked, the 'yes' answer is automatically
            send.

    """
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
@click.argument("qrc_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("res_folders", nargs=-1,
                type=click.Path(exists=True, file_okay=False))
@pass_config
def addqres(config, qrc_path, res_folders, alias, verbose):
    """
    Add <qresource> element with a prefix attribute set to the base name of
    the given folder of resources. All resources contained in this folder are
    recorded in qresource as <file> subelement.

    Args:
        config (:class:`PyqtcliConfig`): PyqtcliConfig object representing
            project config file.
        qrc_path (str): Path to the qrc file that need to add the qresource
            nodes corresponding to `res_folders`.
        res_folders (tuple): Paths to folders of resources to record.
        alias (bool): If True, aliases will be generated while resources are
            recorded.
        verbose (bool): Boolean determining if messages will be displayed.
    """
    qrc_file = read_qrc(qrc_path)
    recorded_dirs = config.get_dirs(qrc_file.name)

    # Remove duplication in res_folders with a set
    res_folders = set(res_folders)

    # Process each resource folders passed
    for folder in res_folders:
        # rel_path => relative path of folder from project directory
        rel_path = os.path.relpath(folder, config.dir_path)

        # Check if given resources folder has already been recorded
        if rel_path in recorded_dirs:
            v.warning("You have already added \'{}\' to {}.".format(
                    folder, qrc_file.name))
            continue

        # Add folder to dirs variable in the config file
        try:
            config.add_dirs(qrc_file.name, rel_path, commit=False)
        except PyqtcliConfigError:
            v.error("{} isn't part of the project.".format(qrc_path))
            raise click.Abort()

        # Add qresource to qrc file
        prefix = get_prefix(folder)
        qrc_file.add_qresource(prefix)
        fill_qresource(qrc_file, folder, prefix)

        v.info("qresource with prefix: \'{}\' has been recorded in {}.".format(
                prefix, qrc_path), verbose)

    qrc_file.build()
    config.save()

    if alias:
        write_alias([qrc_file.path], verbose)


@pyqtcli.command("rmqres", short_help="Remove a <qresource> element in qrc")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.argument("qrc_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("res_folders", nargs=-1,
                type=click.Path(exists=True, file_okay=False))
@pass_config
def rmqres(config, qrc_path, res_folders, verbose):
    """
    Remove a <qresource> element with a prefix attribute set to the base name
    of the given folder of resources. All <file> subelements are removed too.

    Args:
        config (:class:`PyqtcliConfig`): PyqtcliConfig object representing
            project config file.
        qrc_path (str): Path to the qrc file that need to remove the qresource
            nodes corresponding to `res_folders`.
        res_folders (tuple): Paths to folders of resources to remove.
        verbose (bool): Boolean determining if messages will be displayed.
    """
    qrcfile = read_qrc(qrc_path)

    # Remove duplication in res_folders with a set
    res_folders = set(res_folders)

    folders = [os.path.relpath(f, config.dir_path) for f in res_folders]

    # remove folder to dirs variable in the config file
    try:
        config.rm_dirs(qrcfile.name, folders, commit=False)
    except PyqtcliConfigError:
        v.error("{} isn't part of the project.".format(qrc_path))
        raise click.Abort()

    for folder in folders:
        # Remove qresource to qrc file
        prefix = get_prefix(folder)
        qrcfile.remove_qresource(prefix)

        v.info("Resources folder: \'{}\' has been removed in {}.".format(
                folder, qrc_path), verbose)

    config.save()
    qrcfile.build()


@pyqtcli.command("makealias", short_help="Add aliases to qrc's resources")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process")
@click.argument('qrc_files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def makealias(qrc_files, recursive, verbose):
    """Command to generate aliases for each resources contained in qrc files.

    Args:
        qrc_files (tuple): Paths to qrc files that need to generate alias.
        recursive (bool): If True, search recursively qrc filed from launching
            directory.
        verbose (bool): Boolean determining if messages will be displayed.

    """
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_file_search("qrc")

        # Check if recursive option find qrc files
        if not recursive_qrc_files:
            v.error("Could not find any qrc files.")
            raise click.Abort()
        else:
            write_alias(recursive_qrc_files, verbose)

    # Process given files or warns user if none
    if qrc_files:
        write_alias(qrc_files, verbose)
    elif not recursive:
        v.warning("No qrc files was given to process.")


@pyqtcli.command("makerc", short_help="Generate python qrc module to given qrc")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-r", "--recursive", is_flag=True,
              help="Search recursively for qrc files to process.")
@click.argument('qrc_files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def makerc(qrc_files, recursive, verbose):
    """Generate python module for corresponding given qrc files.

    Args:
        qrc_files (tuple): Paths to qrc files that need to generate its
            corresponding rc files.
        recursive (bool): If True, search recursively qrc filed from launching
            directory.
        verbose (bool): Boolean determining if messages will be displayed.

    """
    # Check all qrc files recursively
    if recursive:
        recursive_qrc_files = recursive_file_search("qrc")

        # Check if recursive option find qrc files
        if not recursive_qrc_files:
            v.error("Could not find any qrc files")
        else:
            generate_rc(recursive_qrc_files, verbose)

    # Process given files or warns user if none
    if qrc_files:
        generate_rc(qrc_files, verbose)
    elif not recursive:
        v.warning("No qrc files was given to process.")


@pyqtcli.command("update", short_help="Update project's qrc files")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.option("-p", "--project", is_flag=True, help="update all project's qrcs")
@click.argument('qrc_files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
@pass_config
def update(config, qrc_files, project, verbose):
    """Update project's qrc files through information stored in config file.

    Args:
        config (:class:`PyqtcliConfig`): PyqtcliConfig object representing
            project config file.
        qrc_files (tuple): Paths to qrc files that need to get updated.
        project (bool): If True, all registered qrc files will be updated.
        verbose (bool): Boolean determining if messages will be displayed.

    """
    if project:
        recursive_qrc_files = recursive_file_search("qrc")
        update_project(recursive_qrc_files, config, verbose)
        generate_rc(recursive_qrc_files, verbose)

    elif qrc_files:
        update_project(qrc_files, config, verbose)
        generate_rc(qrc_files, verbose)

    else:
        v.warning("No qrc files to update")
