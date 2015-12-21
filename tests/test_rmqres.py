import os
import shutil
import pytest

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.qrc import read_qrc
from pyqtcli.test.qrc import QRCTestFile
from pyqtcli.exception import QresourceError


def test_simple_rmqres(config, test_resources):
    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new"])

    # Add resources folder config file and qrc
    runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])

    # Remove resources folder config file and qrc
    result = runner.invoke(pyqtcli, ["rmqres", "res.qrc", "resources", "-v"])

    # Parse qrc file
    qrcfile = read_qrc("res.qrc")

    # Check qresource has been deleted
    with pytest.raises(QresourceError) as e:
        qrcfile.get_qresource("/resources")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to '/resources' prefix"
    )

    # Check res_folder has beed removed from dirs variable of config file
    config.read()
    assert config.get_dirs("res.qrc") == []

    assert result.output == (
        "Resources folder: \'resources\' has been removed in res.qrc.\n")


def test_rmqres_with_multiple_res_folders(config, test_resources):
    runner = CliRunner()

    # Copy resources dir to make another resource folder in another directory
    os.mkdir("test")
    shutil.copytree("resources", "test/other_res")

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new"])

    # Add resources folder config file and qrc
    runner.invoke(
        pyqtcli, ["addqres", "res.qrc", "resources", "test/other_res"])

    # Remove resources folder config file and qrc
    runner.invoke(pyqtcli, ["rmqres", "res.qrc", "resources", "test/other_res"])

    # Parse qrc file
    qrcfile = read_qrc("res.qrc")

    # Check qresources has been deleted
    with pytest.raises(QresourceError) as e:
        qrcfile.get_qresource("/resource")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to '/resource' prefix"
    )

    # Check qresources has been deleted
    with pytest.raises(QresourceError) as e:
        qrcfile.get_qresource("/other_res")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to '/other_res' prefix"
    )

    # Check res_folder has beed removed from dirs variable of config file
    config.read()
    assert config.get_dirs("res.qrc") == []


def test_rmqres_with_non_recorded_qrc(config, test_resources):
    runner = CliRunner()

    (
        QRCTestFile("res")
        .add_qresource("/")
        .add_file("test.txt")
        .build()
    )

    result = runner.invoke(pyqtcli, ["rmqres", "res.qrc", "resources"])
    assert result.output.startswith("Error: res.qrc isn't part of the project.")


def test_rmqres_with_non_recorded_res_folder(config, test_resources):
    runner = CliRunner()

    runner.invoke(pyqtcli, ["new"])

    result = runner.invoke(pyqtcli, ["rmqres", "res.qrc", "resources"])
    assert result.output == (
        "Warning: There is no recorded resources folders to delete in res.qrc\n"
    )


def test_delete_recorded_and_not_recorded_res_folders(config, test_resources):
    shutil.copytree("resources", "test")

    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new"])

    # Test addqres with default option
    runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])

    # Remove resources folder config file and qrc
    result = runner.invoke(pyqtcli, ["rmqres", "res.qrc", "test"])
    assert result.output == (
        "Warning: directory 'test' isn't recorded for 'res.qrc' and so "
        "cannot be deleted\n")