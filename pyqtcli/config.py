import os
import click
import configparser

from pyqtcli.exception import PyqtcliConfigError


def find_project_config():
    """Search .pyqtclirc file in the current directory and higher.

    Returns:
        str: Absolute path to the .pyqtclirc and None if not found.
    """
    cwd = "."
    while True:
        for entry in os.scandir(cwd):
            if entry.name == ".pyqtclirc":
                return os.path.abspath(entry.path)

        if os.path.abspath(cwd) == os.path.abspath(os.sep):
            return None

        cwd = "../" + cwd


class PyqtcliConfig():
    """Class to modify and read config file of pyqtcli tool.

    Attributes:
        INI_FILE (str): pyqtcli config file name.
        cparser (configparser.ConfigParser): Ini file parser.
        dir_path (str): Absolute path to config file directory.
        path (str): Absolute path to the config file.
        msg (str): A message to display at the generation of the config
            file.
        verbose (bool): A boolean to determine if a message is displayed at
            the config file generation.

    """

    INI_FILE = ".pyqtclirc"

    def __init__(self, path=None, msg="", verbose=True):
        self.cparser = configparser.ConfigParser()
        self.dir_path = os.getcwd()

        if path:
            self.path = os.path.abspath(path)
        else:
            found_config = find_project_config()
            self.path = found_config or os.path.join(os.getcwd(), self.INI_FILE)

        # Create a new ini file if not exist
        if not os.path.isfile(self.path):
            self.initialize()
            if msg is None or msg == "":
                msg = "The project named: \'{}\' was initialized in {}".format(
                    os.path.basename(os.getcwd()), os.getcwd())

            if verbose:
                click.secho(msg, fg="green", bold=True)

        self.read()

    def initialize(self):
        """Build a basic config file with name and path to PyQt5 project."""
        project_name = os.path.basename(os.getcwd())
        self.cparser.add_section("project")
        self.cparser.set("project", "name", project_name)
        self.cparser.set("project", "path", os.getcwd())
        self.save()

    def read(self):
        """Read the config file."""
        self.cparser.read(self.path)

    def get_qrcs(self):
        """Return a list of qrc names contained in the project config file."""
        self.read()
        sections = self.cparser.sections()
        return [section for section in sections if section.endswith(".qrc")]

    def add_dirs(self, qrc, directories, commit=True):
        """Add a directory to dirs key from given qrc section.

        Args:
            qrc (str): Qrc file name like "res.qrc"
            directories (str or list): Relative paths between directories and
                project dir.
                ex: "\nres\ntest/res\n../res" or ["res"] if one dir in a list
            commit (bool): if true save changes in the config file.

        Raises:
            PyqtcliConfigError: Raised when `qrc` isn't recorded in the
                project config file.

        """
        # Set -> eliminate duplication
        if isinstance(directories, list):
            directories = "\n" + "\n".join(set(directories))
        else:
            if directories.startswith("\n"):
                directories = "\n".join(set(directories.splitlines()))
            else:
                directories = "\n" + "\n".join(set(directories.splitlines()))


        try:
            dirs = self.cparser[qrc].get("dirs", None)
            if dirs is None:
                self.cparser.set(qrc, "dirs", directories)
            else:
                self.cparser.set(qrc, "dirs", dirs + directories)

            if commit:
                self.save()

        except KeyError:
            raise PyqtcliConfigError(
                "Error: No \'{}\' section in .pyqtclirc.".format(qrc))

    def rm_dirs(self, qrc, directories, commit=True):
        """Remove a directory from dirs key in the given qrc section.

        Args:
            qrc (str): Qrc file name like "res.qrc"
            directories (str or list): Relative paths between directories and
                project dir.
                ex: "\nres\ntest/res\n/res" or ["res"] for one dir in a list
            commit (bool): if true save changes in the config file.

        Raises:
            PyqtcliConfigError: Raised when `qrc` isn't recorded in the
                project config file.

        """
        try:
            dirs = self.cparser[qrc].get("dirs", None)

            if not isinstance(directories, list):
                if directories.startswith("\n"):
                    directories = directories.splitlines()[1:]
                else:
                    directories = [directories]

            if dirs is None:  # There is no resources folders recorded yet
                msg = ("Warning: There is no recorded resources folders "
                       "to delete in {}").format(qrc)
                click.secho(msg, fg="yellow", bold=True)
            else:
                # Delete each relative path contains in directory argument
                dirs = self.get_dirs(qrc)
                for rel_path in directories:
                    try:
                        dirs.remove(rel_path)
                    except ValueError:
                        msg = ("Warning: directory \'{}\' isn't recorded "
                               "for \'{}\' and so cannot be deleted".format(
                                   rel_path, qrc))
                        click.secho(msg, fg="yellow", bold=True)

                # Save updated dirs variable
                dirs = "\n".join(dirs)
                if dirs == "":  # Avoid extra '\n' dirs is empty
                    self.cparser.set(qrc, "dirs", dirs)
                else:
                    self.cparser.set(qrc, "dirs", "\n" + dirs)

                if commit:
                    self.save()

        except KeyError:
            raise PyqtcliConfigError(
                "Error: No \'{}\' section in .pyqtclirc.".format(qrc))

    def get_dirs(self, qrc):
        """Return registered resources folders for the given qrc.

        Args:
            qrc (str): Qrc file name like "res.qrc"

        Returns:
            list: A list of relative path to resources folders from project dir.

        """
        dirs = self.cparser.get(qrc, "dirs", fallback=[])
        if dirs == "":
            return []
        else:
            return dirs.splitlines()[1:] if dirs else dirs

    def save(self):
        """Save changes."""
        with open(self.path, "w") as ini:
            self.cparser.write(ini)

    def __str__(self):
        config = ""
        with open(self.path, "r") as f:
            for line in f:
                config += line

        return config
