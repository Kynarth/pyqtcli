import os

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.qrc import read_qrc
from pyqtcli.test.qrc import QRCTestFile


def test_makealias_with_on_file():
    runner = CliRunner()

    # Create false qrc files for testing
    (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("file.txt").add_file("test.txt")
        .add_qresource("/images").add_file("images/icon.png")
        .build()
    )

    # Launch makerc command
    result = runner.invoke(pyqtcli, ["makealias", "-v", "res.qrc"])
    assert result.exit_code == 0

    qrc = read_qrc("res.qrc")

    for res in qrc.list_files():
        assert res.attrib["alias"] == os.path.basename(res.text)


def test_makealias_with_duplication():
    runner = CliRunner()

    # Create false qrc files for testing
    (
        QRCTestFile("res.qrc")
        .add_qresource("/").add_file("file.txt").add_file("test/file.txt")
        .build()
    )

    # Launch makerc command
    result = runner.invoke(pyqtcli, ["makealias", "-v", "res.qrc"])

    # Verify that only first resource get its alias
    qrc = read_qrc("res.qrc")
    files = qrc.list_files()
    assert files[0].attrib.get("alias", None)
    assert files[1].attrib.get("alias", None) is None

    # Check if a warning has been send
    assert ("[WARNING]: Alias \'file.txt\' already exists in \'res.qrc\'"
            " at prefix \'/\'.") in result.output


def test_makealias_recursive():
    runner = CliRunner()

    # Create false qrc files for testing
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource("/").add_file("file.txt")
        .add_qresource("/test").add_file("test/file.txt")
        .build()
    )

    sub_qrc = (
        QRCTestFile("res", "sub")
        .add_qresource("/").add_file("file.txt")
        .add_qresource("/test").add_file("test/file.txt")
        .build()
    )

    sub_sub = (
        QRCTestFile("res", "sub/sub")
        .add_qresource("/").add_file("file.txt")
        .add_qresource("/test").add_file("test/file.txt")
        .build()
    )

    other_sub = (
        QRCTestFile("res", "other")
        .add_qresource("/").add_file("file.txt")
        .add_qresource("/test").add_file("test/file.txt")
        .build()
    )

    qrcs = [qrc, sub_qrc, sub_sub, other_sub]

    # Launch makerc command
    runner.invoke(pyqtcli, ["makealias", "-v", "-r"])

    # Assert all qrc resources get their alias
    for qrc_file in qrcs:
        cur_qrc = read_qrc(qrc_file.path)

        for resource in cur_qrc.list_files():
            assert resource.attrib.get("alias", None)


def test_makealias_recursive_with_no_qrc():
    runner = CliRunner()

    # Launch makerc command
    result = runner.invoke(pyqtcli, ["makealias", "-r"])

    assert result.output.startswith("[ERROR]: Could not find any qrc files.")
