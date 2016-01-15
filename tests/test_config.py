import os
import pytest

from pyqtcli.config import PyqtcliConfig
from pyqtcli.test.verbose import format_msg
from pyqtcli.config import find_project_config
from pyqtcli.exception import PyqtcliConfigError


def test_initial_config_file(config):
    assert config.path == os.path.abspath(".pyqtclirc")
    assert config.dir_path == os.getcwd()

    assert config.cparser.sections() == ['project']
    assert config.cparser.get("project", "name") == "test0"
    assert config.cparser.get("project", "path") == os.getcwd()

    assert str(config) == "[project]\nname = test0\npath = {}\n\n".format(
        os.getcwd())


def test_get_qrcs(config):
    config.cparser.add_section("res.qrc")
    config.cparser.add_section("test.qrc")
    config.cparser.add_section("test")

    assert config.get_qrcs() == ["res.qrc", "test.qrc"]


def test_add_dirs(config):
    config.cparser.add_section("res.qrc")

    # test while dirs key does not exist
    config.add_dirs("res.qrc", "resource")
    assert config.get_dirs("res.qrc") == ["resource"]

    # test dirs has already one value_passing_a_list
    config.add_dirs("res.qrc", ["test/resource"])
    assert config.get_dirs("res.qrc") == ["resource", "test/resource"]

    # test dirs has already two values with multiple dirs
    config.add_dirs("res.qrc", ["../a", "test/other_res"])
    assert sorted(config.get_dirs("res.qrc")) == sorted([
        "resource", "test/resource", "../a", "test/other_res"])


def test_add_dirs_with_nonexistent_qrc_section(config):
    with pytest.raises(PyqtcliConfigError) as e:
        config.add_dirs("test.qrc", "resources")
    assert str(e.value) == "Error: No \'test.qrc\' section in .pyqtclirc."


def test_rm_dirs(config):
    config.cparser.add_section("res.qrc")
    config.add_dirs("res.qrc", "resource")
    config.rm_dirs("res.qrc", "resource")
    assert config.get_dirs("res.qrc") == []


def test_rm_dirs_multiple(config):
    config.cparser.add_section("res.qrc")
    config.add_dirs("res.qrc", ["resource", "test/resource", "../a"])
    config.rm_dirs("res.qrc", ["resource", "../a"])
    assert config.get_dirs("res.qrc") == ["test/resource"]


def test_rm_dirs_nonexistent_dir_in_empty_dirs_key(config, capsys):
    config.cparser.add_section("res.qrc")
    config.rm_dirs("res.qrc", "resources")
    out, err = capsys.readouterr()
    assert format_msg(out) == ("[WARNING]: There is no recorded resources "
                               "folders to delete in res.qrc")
    config.get_dirs("res.qrc") == []


def test_rm_dirs_with_non_recorded_res_folder(config, capsys):
    config.cparser.add_section("res.qrc")
    config.add_dirs("res.qrc", "resources")
    config.rm_dirs("res.qrc", "test")
    out, err = capsys.readouterr()
    assert format_msg(out) == ("[WARNING]: Directory \'test\' isn't "
                               "recorded "
                               "for \'res.qrc\' and so cannot be deleted")
    config.get_dirs("res.qrc") == ["resources"]


def test_rm_dirs_with_nonexistent_qrc_section(config):
    with pytest.raises(PyqtcliConfigError) as e:
        config.rm_dirs("test.qrc", "resources")
    assert str(e.value) == "Error: No \'test.qrc\' section in .pyqtclirc."


def test_add_remove_and_add_again_dirs(config):
    config.cparser.add_section("res.qrc")
    config.add_dirs("res.qrc", "resource")
    config.rm_dirs("res.qrc", "resource")
    config.add_dirs("res.qrc", "resource")
    assert config.get_dirs("res.qrc") == ["resource"]


def test_get_dirs(config):
    assert config.get_dirs("res.qrc") == []

    config.cparser.add_section("res.qrc")
    config.add_dirs("res.qrc", "resources")
    config.add_dirs("res.qrc", "test/resources")

    assert config.get_dirs("res.qrc") == ["resources", "test/resources"]


# noinspection PyUnusedLocal
def test_find_project_config(config):
    found_config = find_project_config()
    assert found_config == os.path.join(os.getcwd(), ".pyqtclirc")


# noinspection PyUnusedLocal
def test_find_project_config_higher_in_tree_directory(config):
    os.rename(".pyqtclirc", "../../.pyqtclirc")
    found_config = find_project_config()
    assert found_config == os.path.join(os.path.abspath("../.."), ".pyqtclirc")
    os.remove("../../.pyqtclirc")


def test_find_nonexistent_project_config():
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
