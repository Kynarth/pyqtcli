import os

from pyqtcli.config import find_project_config
from pyqtcli.config import ProjectConfig


def test_find_project_config_file_in_current_dir():
    open(ProjectConfig.NAME, "a").close()

    assert find_project_config().endswith(".pyqtcli.yml")


def test_find_project_config_file_in_top_directory():
    open(ProjectConfig.NAME, "a").close()
    cfg_path = os.path.join(os.getcwd(), ProjectConfig.NAME)
    os.makedirs("level1/level2")

    # Test with one level depth
    os.chdir("level1")
    assert find_project_config() == cfg_path

    # Test with two level depth
    os.chdir("level2")
    assert find_project_config() == cfg_path


def test_find_project_config_file_in_sub_directory():
    os.mkdir("test")
    open("test/" + ProjectConfig.NAME, "a").close()

    assert find_project_config() is None
