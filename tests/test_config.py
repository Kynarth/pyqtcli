import os

from pyqtcli.config import PyqtcliConfig


def test_default_config():
    PyqtcliConfig()
    assert os.path.isfile(PyqtcliConfig.INI_FILE)


def test_initial_config_file():
    config = PyqtcliConfig()

    assert config.cparser.sections() == ['project']
    assert config.cparser.get("project", "name") == "test0"
    assert config.cparser.get("project", "path") == os.getcwd()
