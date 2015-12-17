import os
import configparser


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

    """

    INI_FILE = ".pyqtclirc"

    def __init__(self, path=None):
        self.cparser = configparser.ConfigParser()

        if path:
            self.path = path
        else:
            found_config = find_project_config()
            self.path = found_config or os.path.join(os.getcwd(), self.INI_FILE)

        # Create a new ini file if not exist
        if not os.path.isfile(self.path):
            self.initialize()

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

    def add_dir(self, qrc, directory, commit=True):
        """Add a directory to dirs key from given qrc section.

        Args:
            qrc (str): Qrc file name like "res.qrc"
            directory (str): Relative path between directory to add and qrc.
            commit (bool): if true save changes in the config file.

        Returns:
            bool: True if the operation is successfull otherwise False.

        """
        try:
            dirs = self.cparser[qrc].get("dirs", None)
            if dirs is None:
                self.cparser.set(qrc, "dirs", directory)
            else:
                self.cparser.set(qrc, "dirs", dirs + ", " + directory)

            if commit:
                self.save()

            return True
        except KeyError:
            return False

    def get_dirs(self, qrc):
        """Return registered resources dirs for the given qrc

        Args:
            qrc (str): Qrc file name like "res.qrc"

        Returns:
            list: A list of relative path to resources folders from qrc file.
        """
        dirs = self.cparser.get(qrc, "dirs", fallback=[])
        return dirs.split(", ") if dirs else dirs

    def save(self):
        """Save changes."""
        with open(self.path, "w") as ini:
            self.cparser.write(ini)
