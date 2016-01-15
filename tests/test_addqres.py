import os
import shutil

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.qrc import read_qrc
from pyqtcli.test.qrc import QRCTestFile
from pyqtcli import verbose as v


def test_simple_addqres(config, test_resources):
    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new", "qrc"])

    # Test addqres with default option
    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])
    assert result.exit_code == 0

    # Parse qrc file
    qrcfile = read_qrc("res.qrc")

    # Check qresource has been added
    qrcfile.get_qresource("/resources")

    # Check file subelements in qresource
    resources = qrcfile.list_resources("/resources")

    for root, dirs, files in os.walk("resources"):
        for f in files:
            assert os.path.join(root, f) in resources

    assert len(resources) == test_resources

    # Check res_folder has been added to dirs variable of config file
    config.read()
    config.get_dirs("res.qrc") == ["resources"]


def test_complex_addqres(config, test_resources):
    runner = CliRunner()

    # Make a new dir to complicate path between resources folder and qrc file
    os.mkdir("test")
    shutil.move("resources", "test")

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new", "qrc", "../res.qrc"])

    result = runner.invoke(
            pyqtcli, ["addqres", "-a", "-v", "../res.qrc", "test/resources"]
    )
    assert result.exit_code == 0

    # Get in res.qrc directory
    os.chdir("..")

    # Parse qrc file
    qrcfile = read_qrc("res.qrc")

    # Check qresource has been added
    qrcfile.get_qresource("/resources")

    # Check file subelements in qresource
    resources = qrcfile.list_resources("/resources")

    for root, dirs, files in os.walk("test/resources"):
        for f in files:
            assert os.path.join(root, f) in resources

    assert len(resources) == test_resources

    # Check res_folder has been added to dirs variable of config file
    config.read()
    assert config.get_dirs("res.qrc") == ["test/resources"]

    # Check resources' alias
    files = qrcfile.list_files("/resources")

    for resource in files:
        assert os.path.basename(resource.text) == resource.attrib["alias"]


def test_addqres_two_times(config, test_resources):
    runner = CliRunner()

    # Copy resources dir to make another resource folder in another directory
    os.mkdir("test")
    shutil.copytree("resources", "test/other_res")

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new", "qrc", "res.qrc"])

    # Create to qresources in res.qrc
    runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])
    runner.invoke(pyqtcli, ["addqres", "-a", "res.qrc", "test/other_res"])

    # Parse qrc file
    qrcfile = read_qrc("res.qrc")

    # Check qresources has been added
    qrcfile.get_qresource("/resources")
    qrcfile.get_qresource("/other_res")

    # Check file subelements in qresource "/resources"
    resources = qrcfile.list_resources("/resources")

    for root, dirs, files in os.walk("resources"):
        for f in files:
            assert os.path.join(root, f) in resources

    assert len(resources) == test_resources

    # Check file subelements in qresource "/other_res"
    resources = qrcfile.list_resources("/other_res")

    for root, dirs, files in os.walk("test/other_res"):
        for f in files:
            assert os.path.join(root, f) in resources

    assert len(resources) == test_resources

    # Check resources' alias in other_res qresource
    files = qrcfile.list_files("/other_res")

    for resource in files:
        assert os.path.basename(resource.text) == resource.attrib["alias"]

    # Check that the two res folders have been added to dirs variable of
    # config file
    config.read()
    assert sorted(config.get_dirs("res.qrc")) == sorted([
        "resources", "test/other_res"])


def test_addqres_with_two_res_folders(config, test_resources):
    runner = CliRunner()

    # Copy resources dir to make another resource folder in another directory
    os.mkdir("test")
    shutil.copytree("resources", "test/other_res")

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new", "qrc", "res.qrc"])

    # Create to qresources in res.qrc
    runner.invoke(
            pyqtcli, ["addqres", "res.qrc", "resources", "test/other_res"])

    # Parse qrc file
    qrcfile = read_qrc("res.qrc")

    # Check qresources has been added
    qrcfile.get_qresource("/resources")
    qrcfile.get_qresource("/other_res")

    # Check file subelements in qresource "/resources"
    resources = qrcfile.list_resources("/resources")

    for root, dirs, files in os.walk("resources"):
        for f in files:
            assert os.path.join(root, f) in resources

    assert len(resources) == test_resources

    # Check file subelements in qresource "/other_res"
    resources = qrcfile.list_resources("/other_res")

    for root, dirs, files in os.walk("test/other_res"):
        for f in files:
            assert os.path.join(root, f) in resources

    assert len(resources) == test_resources

    # Check that the two res folders have been added to dirs variable of
    # config file
    config.read()
    assert sorted(config.get_dirs("res.qrc")) == sorted([
        "resources", "test/other_res"])


# noinspection PyUnusedLocal
def test_addqres_in_non_project_qrc(config, test_resources):
    runner = CliRunner()

    QRCTestFile("res").add_qresource("/").add_file("test.txt").build()

    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])
    assert result.output == v.error(
            "res.qrc isn't part of the project.\nAborted!\n")


# noinspection PyUnusedLocal
def test_addqres_duplication(config, test_resources):
    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new", "qrc"])

    # Add qresources corresponding to resources folder
    runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])

    # Add the same qresource
    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])

    assert result.output == v.warning(
            "You have already added \'resources\' to res.qrc.\n")
