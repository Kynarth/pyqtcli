import os
import re
import pytest

from click.testing import CliRunner

from tests.qrc import TestQRCFile


def test_simple_qrc():
    with CliRunner().isolated_filesystem():
        qrc = TestQRCFile("res").add_qresource().add_file("file.txt").build()

        assert os.path.isfile(qrc.path)


def test_complexe_qrc():
    with CliRunner().isolated_filesystem():
        qrc = (
            TestQRCFile("res", "sub_dir")
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
                TestQRCFile("res")
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
                TestQRCFile("res")
                .add_qresource().add_file("file.txt")
                .add_qresource().add_file("images/test.txt")
                .build()
            )
        assert regex.search(str(e)).group() == (
            "Error: Qresource with prefix: 'None' already exists."
        )
