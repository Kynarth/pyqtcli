import os

from pyqtcli.config import PyqtcliConfig
from pyqtcli.config import find_project_config


def test_initial_config_file(config):
    assert config.cparser.sections() == ['project']
    assert config.cparser.get("project", "name") == "test0"
    assert config.cparser.get("project", "path") == os.getcwd()


def test_get_qrcs(config):
    config.cparser.add_section("res")
    config.cparser.add_section("test")

    assert config.get_qrcs() == ["res", "test"]


def test_find_project_config(config):
    found_config = find_project_config()
    assert found_config == os.path.join(os.getcwd(), ".pyqtclirc")


def test_find_project_config_higher_in_tree_directory(config):
    os.rename(".pyqtclirc", "../../.pyqtclirc")
    found_config = find_project_config()
    assert found_config == os.path.join(os.path.abspath("../.."), ".pyqtclirc")
    os.remove("../../.pyqtclirc")


def test_find_nonexistant_project_config():
    assert find_project_config() is None


def test_get_existing_config_file(config):
    # Modify base config file
    config.cparser.add_section("test")
    config.save()

    # Create sub dir and get in
    os.mkdir("test")
    os.chdir("test")

    # Retrieve created config file
    found_config = PyqtcliConfig()
    assert found_config.cparser.sections() == ["project", "test"]
