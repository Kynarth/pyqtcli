import os

from lxml import etree
from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.qrc import read_qrc
from pyqtcli import verbose as v
from pyqtcli.test.verbose import format_msg


def test_new_default(config):
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["new", "qrc", "-v"])

    # Check qrc file is generated
    assert result.exit_code == 0
    assert os.path.isfile("res.qrc")

    # Check content of newly generated qrc file
    tree = etree.parse("res.qrc")
    assert etree.tostring(tree) == b"<RCC/>"

    # Check qrc file has been added to project the config file
    config.read()
    assert ["res.qrc"] == config.get_qrcs()

    # Test verbose
    assert format_msg(result.output) == v.info(
            "Qrc file \'res.qrc\' has been created.\n")


def test_new_qrc(config):
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["new", "qrc", "qrc/test.qrc"])

    assert result.exit_code == 0
    assert os.path.isfile("qrc/test.qrc")

    # Check content of newly generated qrc file
    tree = etree.parse("qrc/test.qrc")
    assert etree.tostring(tree) == b"<RCC/>"

    # Check qrc file has been added to project the config file
    config.read()
    assert ["test.qrc"] == config.get_qrcs()


# noinspection PyUnusedLocal
def test_new_qrc_from_folder(config, test_resources):
    runner = CliRunner()

    # launch makerc command
    runner.invoke(pyqtcli, ["new", "qrc", "test.qrc", "resources"])

    assert os.path.isfile("test.qrc")

    qrc = read_qrc("test.qrc")

    # Check qresources and their prefix attribute corresponding to
    # directories of the first level of resources folder
    first_dirs = [
        "/" + d for d in os.listdir("resources")
        if os.path.isdir(os.path.join("resources", d))
    ]
    first_dirs.append("/")

    for qresource in qrc.qresources:
        assert qresource.attrib.get("prefix", None) in first_dirs
        directory = first_dirs.pop(
            first_dirs.index(qresource.attrib.get("prefix"))
        )

        # Get all resources files contained in the current qresource
        res = qrc.list_resources(qresource.attrib["prefix"])

        # Special case for root directory to not get into sub directories
        if directory == "/":
            resources = [
                os.path.join("resources", r)
                for r in os.listdir("resources")
                if os.path.isfile(os.path.join("resources", r))
            ]

            for resource in resources:
                assert resource in res

            continue

        # Search if resource files have been recorded correctly in other
        # directories
        for root, dirs, files in os.walk("resources" + directory):
            for file_path in files:
                assert os.path.join(root, file_path) in res

    # Verify if all dirs have been checked
    assert first_dirs == []


def test_two_new_qrcs(config):
    runner = CliRunner()
    runner.invoke(pyqtcli, ["new", "qrc"])
    runner.invoke(pyqtcli, ["new", "qrc", "qrc/test.qrc"])
    assert ["res.qrc", "test.qrc"] == config.get_qrcs()


def test_new_duplication():
    runner = CliRunner()
    runner.invoke(pyqtcli, ["new", "qrc"])
    result = runner.invoke(pyqtcli, ["new", "qrc"])
    assert format_msg(result.output).startswith(
        "[ERROR]: A qrc file named \'res.qrc\' already exists"
    )
