import os
import re
import pytest

from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.test.qrc import QRCTestFile


def test_simple_qrc():
    with CliRunner().isolated_filesystem():
        qrc = QRCTestFile("res").add_qresource().add_file("file.txt").build()

        assert os.path.isfile(qrc.path)


def test_complexe_qrc():
    with CliRunner().isolated_filesystem():
        qrc = (
            QRCTestFile("res", "sub_dir")
            .add_qresource().add_file("file.txt").add_file("test.txt")
            .add_qresource("/images").add_file("image/icon.png")
            .add_qresource("/json").add_file("resource/json/test.json")
            .add_file("images/logo.png", "/images")
            .build()
        )

        assert os.path.isfile(qrc.path)


def test_nonexistent_qresource():
    regex = re.compile(r"Error:.*")
    with CliRunner().isolated_filesystem():
        with pytest.raises(BaseException) as e:
            (
                QRCTestFile("res")
                .add_qresource().add_file("file.txt")
                .add_qresource("/images").add_file("images/test.txt")
                .add_file("test.txt", "prefix")
                .build()
            )
        assert regex.search(str(e)).group() == (
            "Error: Qresource with prefix: 'prefix' does not exist."
        )


def test_duplication_of_qresource():
    regex = re.compile(r"Error:.*")
    with CliRunner().isolated_filesystem():
        with pytest.raises(SystemExit) as e:
            (
                QRCTestFile("res")
                .add_qresource().add_file("file.txt")
                .add_qresource().add_file("images/test.txt")
                .build()
            )
        assert regex.search(str(e)).group() == (
            "Error: Qresource with prefix: 'None' already exists."
        )


def test_qrc_command(qrc_contents):
    runner = CliRunner()
    # Location of resource folder for testing
    abs_res_folder = os.path.abspath("tests/resources")

    with runner.isolated_filesystem():
        # launch makerc command
        result = runner.invoke(
            pyqtcli, ["qrc", "-v", abs_res_folder, "-o", "test"]
        )

        # Check if qrc file is generated
        print("verbose:\n" + result.output)
        assert os.path.isfile("test.qrc")

        # Check qrc contents
        with open("test.qrc", "r") as qrc:
            for x, y in zip(qrc, qrc_contents.split("\n")):
                assert x.strip() == y.strip()
