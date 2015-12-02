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
    assert "res" in config.cparser.sections()


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
    assert "test" in config.cparser.sections()
