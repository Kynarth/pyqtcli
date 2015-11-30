import os
import configparser


class PyqtcliConfig():
    """Class to modify and read config file of pyqtcli tool.

    Attributes:
        INI_FILE (str): pyqtcli config file name.
        cparser (configparser.ConfigParser): Ini file parser.

    """

    INI_FILE = ".pyqtclirc"

    def __init__(self):
        self.path = os.path.join(os.getcwd(), self.INI_FILE)
        self.cparser = configparser.ConfigParser()
        self.initialize()
        self.cparser.read(self.INI_FILE)

    def initialize(self):
        """Build a basic config file with name and path to PyQt5 project."""
        project_name = os.path.basename(os.getcwd())
        self.cparser.add_section("project")
        self.cparser.set("project", "name", project_name)
        self.cparser.set("project", "path", os.getcwd())
        self.save()

    def save(self):
        """Save changes."""
        with open(self.path, "w") as ini:
            self.cparser.write(ini)
