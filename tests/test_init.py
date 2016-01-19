import os
import yaml

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.config import ProjectConfig


def test_init_with_default_option():
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ['init'])

    assert result.output.startswith("[INFO]: The project named: \'test0\'")
    assert os.path.isfile(ProjectConfig.NAME)


def test_init_quiet_option():
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init", "-q"])

    assert result.output == ""
    assert os.path.isfile(ProjectConfig.NAME)


def test_init_reset_without_yes_option_nor_input():
    cfg = ProjectConfig()
    cfg._config['project'] = "name"
    cfg._config['path'] = "path"
    cfg.save()

    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init"])

    assert result.output == (
        "Do you want to reset pyqtcli config? [y/N]: \n"
        "Aborted!\n"
    )
    assert result.exit_code == 1

    # Check if the config file has not been reset
    with open(ProjectConfig.NAME, "r") as f:
        yml = yaml.load(f)

    assert yml["project"] == "name"
    assert yml["path"] == "path"


def test_init_reset_yes_option():
    cfg = ProjectConfig()
    cfg._config['project'] = "name"
    cfg._config['path'] = "path"
    cfg.save()

    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init", "-y"])

    assert result.exit_code == 0
    assert result.output.startswith("[INFO]: Pyqtcli config reset")

    # Check if the config file has been correctly reset
    with open(ProjectConfig.NAME, "r") as f:
        yml = yaml.load(f)

    assert yml["project"] == "test0"
    assert yml["path"] == os.getcwd()


def test_init_reset_yes_answer():
    cfg = ProjectConfig()
    cfg._config['project'] = "name"
    cfg._config['path'] = "path"
    cfg.save()

    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init"], input="y")

    assert result.output.endswith("[INFO]: Pyqtcli config reset\n")
    assert result.exit_code == 0

    # Check if the config file has been correctly reset
    with open(ProjectConfig.NAME, "r") as f:
        yml = yaml.load(f)

    assert yml["project"] == "test0"
    assert yml["path"] == os.getcwd()


def test_init_reset_with_negative_answer():
    cfg = ProjectConfig()
    cfg._config['project'] = "name"
    cfg._config['path'] = "path"
    cfg.save()

    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["init"], input="n")

    assert result.exit_code == 1

    # Check if the config file has not been reset
    with open(ProjectConfig.NAME, "r") as f:
        yml = yaml.load(f)

    assert yml["project"] == "name"
    assert yml["path"] == "path"
