from click.testing import CliRunner

from pyqtcli.cli import pyqtcli


def test_new_command_with_default_option():
    runner = CliRunner()
    result = runner.invoke(pyqtcli, ["new"])
    assert result.exit_code == 0
