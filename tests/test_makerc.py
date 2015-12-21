import os

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.test.qrc import QRCTestFile


def test_makerc_with_on_file():
    runner = CliRunner()

    qrc = (
        QRCTestFile("res").add_qresource("/")
        .add_file("file.txt").build()
    )

    # Launch makerc command
    result = runner.invoke(pyqtcli, ["makerc", "-v", qrc.path])
    assert result.exit_code == 0

    assert os.path.isfile("res_rc.py")


def test_makerc_with_two_files_in_same_directory():
    runner = CliRunner()

    qrc = (
        QRCTestFile("res").add_qresource("/")
        .add_file("file.txt")
        .build()
    )

    qrc_bis = (
        QRCTestFile("res_bis").add_qresource("/")
        .add_file("file_bis.txt")
        .build()
    )

    # Launch makerc command
    runner.invoke(pyqtcli, ["makerc", "-v", qrc.path, qrc_bis.path])

    assert os.path.isfile("res_rc.py")
    assert os.path.isfile("res_bis_rc.py")


def test_makerc_with_3_files_in_different_dirs():
    runner = CliRunner()

    # Create dir to test qrc file in upper levels
    os.mkdir("test_dir")
    os.chdir("test_dir")

    qrc = (
        QRCTestFile("res").add_qresource("/test_dir")
        .add_file("file.txt").build()
    )

    qrc_top = (
        QRCTestFile("res_top", "../").add_qresource("/")
        .add_file("file_top.txt").build()
    )

    qrc_down = (
        QRCTestFile("res_down", "down")
        .add_qresource("/test_dir/down")
        .add_file("down/file_down.txt").build()
    )

    # Launch makerc command
    runner.invoke(
        pyqtcli, ["makerc", "-v", qrc.path, qrc_top.path, qrc_down.path]
    )

    assert os.path.isfile("res_rc.py")
    assert os.path.isfile("../res_top_rc.py")
    assert os.path.isfile("down/res_down_rc.py")


def test_makerc_recursive_option():
    runner = CliRunner()

    (
        QRCTestFile("res").add_qresource("/")
        .add_file("file.txt")
        .build()
    )

    (
        QRCTestFile("res_bis", "qrc_dir").add_qresource("/qrc_dir")
        .add_file("qrc_dir/file_bis.txt")
        .build()
    )

    (
        QRCTestFile("res_ter", "dir1/dir2").add_qresource("/dir1/dir2")
        .add_file("dir1/dir2/file_ter.txt")
        .build()
    )

    # Launch makerc command
    runner.invoke(pyqtcli, ["makerc", "-v", "-r"])

    assert os.path.isfile("res_rc.py")
    assert os.path.isfile("qrc_dir/res_bis_rc.py")
    assert os.path.isfile("dir1/dir2/res_ter_rc.py")


def test_makerc_with_invalid_qrc_file():
    runner = CliRunner()

    open("invalid.qrc", "a").close()

    result = runner.invoke(pyqtcli, ["makerc", "-v", "invalid.qrc"])
    print(result.output)
    assert result.exit_code != 0
