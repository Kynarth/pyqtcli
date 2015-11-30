import os

from pyqtcli.cli import pyqtcli
from click.testing import CliRunner
from pyqtcli.config import PyqtcliConfig


def test_init():
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init"])

    assert result.output.startswith("Pyqtcli initialized")
    assert os.path.isfile(PyqtcliConfig.INI_FILE)


def test_init_quiet_option():
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init", "-q"])

    assert result.output == ""
    assert os.path.isfile(PyqtcliConfig.INI_FILE)


def test_init_reset_without_yes_option_nor_input():
    PyqtcliConfig()
    runner = CliRunner()

    result = runner.invoke(pyqtcli, ["init"])
    assert result.exit_code == 1


def test_init_reset_yes_option():
    PyqtcliConfig()
    runner = CliRunner()

    result = runner.invoke(pyqtcli, ["init", "-y"])
    assert result.exit_code == 0
    assert result.output.startswith("Pyqtcli config reset")


def test_init_reset_yes_answer():
    PyqtcliConfig()
    runner = CliRunner()

    result = runner.invoke(pyqtcli, ["init"], input="y")
    assert result.output.endswith("Pyqtcli config reset\n")
    assert result.exit_code == 0


def test_init_reset_with_no_answer():
    PyqtcliConfig()
    runner = CliRunner()

    result = runner.invoke(pyqtcli, ["init"], input="n")
    assert result.exit_code == 1
