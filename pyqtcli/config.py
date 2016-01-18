import os
import yaml

from pyqtcli import verbose as v


def find_project_config():
    """Search .pyqtcli.yml file in the current directory or higher.

    Returns:
        str: Absolute path to the .pyqtclirc and None if not found.

    """
    cwd = "."
    while True:
        for entry in os.scandir(cwd):
            if entry.name == ProjectConfig.NAME:
                return os.path.abspath(entry.path)

        if os.path.abspath(cwd) == os.path.abspath(os.sep):
            return None

        cwd = "../" + cwd


class ProjectConfig:
    """Wrapper for the project config file to easily read and modify it.

    Attributes:
        path (Optional[str]): Absolute path to the config file.
        msg (Optional[str]): A message to display at the generation of the
            config file.
        verbose (Optional[bool]): A boolean to determine if a message is
            displayed at the config file generation.
        dir_path (str): Absolute path to config file directory.
        path (str): Absolute path to config file.

    """

    NAME = ".pyqtcli.yml"

    def __init__(self, path=".", msg="", verbose=True):
        self._config = {}

        if path != ".":
            self._dir_path = os.path.abspath(path)
            self._path = os.path.join(self._dir_path, self.NAME)
        else:
            # Search for an already existent config file
            self._path = find_project_config()
            if self.path:
                self._dir_path = os.path.dirname(self._path)
                self.read()  # Load found config file
            else:
                self._dir_path = os.getcwd()
                self._path = os.path.join(self._dir_path, self.NAME)

        # Create a new config file if nonexistent
        if not os.path.isfile(self._path):
            self.initialize()

            if msg is None or msg == "":
                msg = "The project named: \'{}\' was initialized in {}".format(
                    os.path.basename(os.getcwd()), os.getcwd())

            v.info(msg, verbose)

    def initialize(self):
        """Build a basic config file with name and path to PyQt5 project."""
        project_name = os.path.basename(self._dir_path)
        self._config = {"project": project_name, "path": self._dir_path}
        self.save()

    def read(self):
        """Read the config file."""
        with open(self._path, "r") as cfg:
            self._config = yaml.load(cfg)

    def save(self):
        """Save config attribute in yml file."""
        with open(self._path, "w") as cfg:
            yaml.dump(self._config, cfg)

    @property
    def dir_path(self):
        return self._dir_path

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._config.get("project", None)

    @property
    def config(self):
        return self._config
