import os
import re
import pytest
import shutil

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.qrc import read_qrc
from pyqtcli.test.qrc import QRCTestFile
from pyqtcli.exception import QresourceError


# noinspection PyUnusedLocal
def test_update_with_removed_a_resources_folder(config, test_resources):
    runner = CliRunner()

    # Generate a qrc file from a resources folder
    runner.invoke(pyqtcli, ["new", "qrc", "res.qrc", "resources"])

    # Remove images directory from resources folder
    shutil.rmtree("resources/images")

    # Update the qrc file
    runner.invoke(pyqtcli, ["update", "res.qrc"])

    # Check that qresource corresponding to images folder has been removed
    qrc = read_qrc("res.qrc")
    with pytest.raises(QresourceError):
        qrc.get_qresource("/images")

    # Check corresponding rc has been generated
    assert os.path.isfile("res_rc.py")


# noinspection PyUnusedLocal
def test_update_with_added_a_resources_folder(test_resources):
    runner = CliRunner()

    # Generate a qrc file from a resources folder
    runner.invoke(pyqtcli, ["new", "qrc", "res.qrc", "resources"])

    # Add directory with resources
    os.mkdir("resources/images/test")
    open("resources/images/test/test.txt", 'a').close()
    open("resources/images/test/bye.txt", 'a').close()
    open("resources/images/test/yahooo.txt", 'a').close()

    # Update the qrc file
    runner.invoke(pyqtcli, ["update", "res.qrc"])

    # Check that resources corresponding to test folder has been added to
    # qresource corresponding to '/images' prefix
    qrc = read_qrc("res.qrc")
    assert sorted(qrc.list_resources("/images")) == sorted([
        "resources/images/banner.png",
        "resources/images/toolbar/search.svg",
        "resources/images/toolbar/quit.svg",
        "resources/images/toolbar/new.svg",
        "resources/images/assets/test.bmp",
        "resources/images/assets/fg.bmp",
        "resources/images/assets/bg.bmp",
        "resources/images/test/yahooo.txt",
        "resources/images/test/bye.txt",
        "resources/images/test/test.txt"
    ])

    # Check corresponding rc has been generated
    assert os.path.isfile("res_rc.py")


# noinspection PyUnusedLocal
def test_update_with_project_option(test_resources):
    runner = CliRunner()

    # Generate a second folder of resources
    os.mkdir("test_dir")
    open("test_dir/file.txt", "a").close()
    open("test_dir/test.txt", "a").close()

    # Generate qrc files from a resources folder
    runner.invoke(pyqtcli, ["new", "qrc", "res.qrc", "resources"])
    runner.invoke(pyqtcli, ["new", "qrc", "test.qrc", "test_dir"])

    # Add files to modify res.qrc and test.qrc
    open("resources/test.txt", "a").close()
    open("test_dir/yahoo.txt", "a").close()

    # Update the qrc file
    runner.invoke(pyqtcli, ["update", "-p"])

    # Check that resources corresponding to test folder has been added to
    # qresource corresponding to '/images' prefix
    qrc = read_qrc("res.qrc")
    test_qrc = read_qrc("test.qrc")

    assert sorted(qrc.list_resources("/")) == sorted([
        "resources/file.txt",
        "resources/test.txt"
    ])

    assert sorted(test_qrc.list_resources("/")) == sorted([
        "test_dir/file.txt",
        "test_dir/test.txt",
        "test_dir/yahoo.txt"
    ])

    # Check corresponding rc has been generated
    assert os.path.isfile("res_rc.py")
    assert os.path.isfile("test_rc.py")


# noinspection PyUnusedLocal
def test_update_with_qrc_recording_res_in_project_dir(config):
    runner = CliRunner()

    qrc = QRCTestFile("res.qrc").add_qresource().add_file("file.txt").build()

    # Add file to modify res.qrc
    open("test.txt", "a").close()

    config.cparser.add_section("res.qrc")
    config.add_dirs("res.qrc", ".")

    # Update the qrc file
    result = runner.invoke(pyqtcli, ["update", "res.qrc"])

    # Check that resources corresponding to test folder has been added to
    # qresource corresponding to '/images' prefix
    qrc = read_qrc("res.qrc")

    assert qrc.list_resources("/") == ["file.txt"]

    regex = re.compile("\n\s+")
    assert (
        "[WARNING]: Can't update automatically a qrc file where "
        "resources are in the same directory as the project one.\n"
    ) == regex.sub(" ", result.output)

    # Check corresponding rc has been generated
    assert os.path.isfile("res_rc.py")
