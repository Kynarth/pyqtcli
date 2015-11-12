import os

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from tests.qrc import TestQRCFile


def test_makerc_with_on_file():
    runner = CliRunner()

    with runner.isolated_filesystem():
        qrc = (
            TestQRCFile("res").add_qresource("/")
            .add_file("file.txt").build()
        )

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", qrc.path]
        )

        print("\n===================== Test with one file ====================")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(qrc.path)


def test_makerc_with_two_files_in_same_directory():
    runner = CliRunner()

    with runner.isolated_filesystem():
        qrc = (
            TestQRCFile("res").add_qresource("/")
            .add_file("file.txt").build()
        )

        qrc_bis = (
            TestQRCFile("res_bis").add_qresource("/")
            .add_file("file_bis.txt").build()
        )

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", qrc.path, qrc_bis.path]
        )

        print("\n============== Test with two files on same dir ==============")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(qrc.path)
        assert os.path.isfile(qrc_bis.path)


def test_makerc_with_3_files_in_different_dirs():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create dir to test qrc file in upper levels
        os.mkdir("test_dir")
        os.chdir("test_dir")

        qrc = (
            TestQRCFile("res").add_qresource("/test_dir")
            .add_file("file.txt").build()
        )

        qrc_top = (
            TestQRCFile("res_top", "../").add_qresource("/")
            .add_file("file_top.txt").build()
        )

        qrc_down = (
            TestQRCFile("res_down", "down")
            .add_qresource("/test_dir/down")
            .add_file("file_down.txt").build()
        )

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", qrc.path, qrc_top.path, qrc_down.path]
        )

        print("\n============ Test with 3 files on different dirs ============")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(qrc.path)
        assert os.path.isfile(qrc_top.path)
        assert os.path.isfile(qrc_down.path)


def test_makerc_recursive_option():
    runner = CliRunner()

    with runner.isolated_filesystem():
        qrc = (
            TestQRCFile("res").add_qresource("/")
            .add_file("file.txt").build()
        )

        qrc_bis = (
            TestQRCFile("res_bis", "qrc_dir").add_qresource("/qrc_dir")
            .add_file("file_bis.txt").build()
        )

        qrc_ter = (
            TestQRCFile("res_ter", "dir1/dir2").add_qresource("/dir1/dir2")
            .add_file("file_ter.txt").build()
        )

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", "-r"]
        )

        print("\n================== Test recursive option ====================")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(qrc.path)
        assert os.path.isfile(qrc_bis.path)
        assert os.path.isfile(qrc_ter.path)
