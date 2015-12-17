import os
import shutil

from lxml import etree
from pyqtcli.cli import pyqtcli
from click.testing import CliRunner
from pyqtcli.test.qrc import QRCTestFile


def test_simple_addqres(config, resources):
    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new"])

    # test addqres with default option
    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])
    assert result.exit_code == 0

    # Parse qrc file
    tree = etree.parse("res.qrc")
    root = tree.getroot()

    # Check qresource has been added
    qres_prefix = []  # Elements matching qresource with prefix = '/resources'
    for qresource in root.iter(tag="qresource"):
        if qresource.attrib.get("prefix") == "/resources":
            qres_prefix.append(qresource)
    assert len(qres_prefix) == 1

    # Check file subelement in qresource
    rel_path = os.path.relpath("resources", ".")
    nb_res = 0
    for resource in qres_prefix[0].iter(tag="file"):
        assert resource.text.startswith(rel_path)
        nb_res += 1
    assert nb_res == resources

    # Check res_folder has beed added to dirs variable of config file
    config.read()
    assert config.cparser["res.qrc"].get("dirs") == "resources"


def test_complexe_addqres(config, resources):
    runner = CliRunner()

    # Make a new dir to complexify path between resources folder and qrc file
    os.mkdir("test")
    shutil.move("resources", "test")

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new", "../res.qrc"])

    # test addqres with default option
    result = runner.invoke(
        pyqtcli, ["addqres", "-a", "-v", "../res.qrc", "test/resources"]
    )
    assert result.exit_code == 0

    # Parse qrc file
    tree = etree.parse("../res.qrc")
    root = tree.getroot()

    # Check qresource has been added
    qres_prefix = []  # Elements matching qresource with prefix = '/resources'
    for qresource in root.iter(tag="qresource"):
        if qresource.attrib.get("prefix") == "/resources":
            qres_prefix.append(qresource)
    assert len(qres_prefix) == 1

    # Check file subelement in qresource
    rel_path = os.path.relpath("test/resources", "..")
    nb_res = 0
    for resource in qres_prefix[0].iter(tag="file"):
        assert resource.text.startswith(rel_path)
        nb_res += 1
    assert nb_res == resources

    # Check res_folder has beed added to dirs variable of config file
    config.read()
    assert config.cparser["res.qrc"].get("dirs") == "test0/test/resources"


def test_addqres_in_non_project_qrc(config, resources):
    runner = CliRunner()

    (
        QRCTestFile("res")
        .add_qresource("/")
        .add_file("test.txt")
        .build()
    )

    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])
    assert result.output.startswith("Qrc: res.qrc isn't part of the project.")


def test_addqres_duplication(config, resources):
    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new"])

    # Add qresources corresponding to resources folder
    runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])

    # Add the same qresource
    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])

    assert result.output.startswith(
        "You have already added this resources folder to res.qrc."
    )
