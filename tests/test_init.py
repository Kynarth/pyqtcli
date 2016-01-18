from click.testing import CliRunner

from pyqtcli.cli import pyqtcli


def test_init_with_default_option():
    runner = CliRunner()

    result = runner.invoke(pyqtcli, ['init'])
    assert result.exit_code == 0
