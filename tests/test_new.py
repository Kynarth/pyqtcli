import os

from lxml import etree
from pyqtcli.cli import pyqtcli
from click.testing import CliRunner


def test_new_default(config):
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["new"])

    # Check qrc file is generated
    assert result.exit_code == 0
    assert os.path.isfile("res.qrc")

    # Check content of newly generated qrc file
    tree = etree.parse("res.qrc")
    assert etree.tostring(tree) == b"<RCC/>"

    # Check qrc file has been added to project the config file
    config.read()
    assert ["res.qrc"] == config.get_qrcs()


def test_new_qrc(config):
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["new", "--qrc", "qrc/test.qrc"])

    assert result.exit_code == 0
    assert os.path.isfile("qrc/test.qrc")

    # Check content of newly generated qrc file
    tree = etree.parse("qrc/test.qrc")
    assert etree.tostring(tree) == b"<RCC/>"

    # Check qrc file has been added to project the config file
    config.read()
    assert ["test.qrc"] == config.get_qrcs()


def test_two_new_qrcs(config):
    runner = CliRunner()
    runner.invoke(pyqtcli, ["new"])
    runner.invoke(pyqtcli, ["new", "--qrc", "qrc/test.qrc"])
    assert ["res.qrc", "test.qrc"] == config.get_qrcs()


def test_new_duplication(config):
    runner = CliRunner()
    runner.invoke(pyqtcli, ["new"])
    result = runner.invoke(pyqtcli, ["new"])
    assert result.output.startswith(
        "A qrc file named \'res.qrc\' already exists"
    )
