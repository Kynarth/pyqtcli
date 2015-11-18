import os
import re
import pytest

from lxml import etree
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


def test_qrc_command():
    runner = CliRunner()
    # Location of resource folder for testing
    abs_res_folder = os.path.abspath("tests/resources")

    with runner.isolated_filesystem():
        # Relative path to resource folder from test folder
        rel_res_folder = os.path.relpath(abs_res_folder)

        # launch makerc command
        result = runner.invoke(
            pyqtcli, ["qrc", "-v", abs_res_folder, "-o", "test"]
        )

        # Check if qrc file is generated
        print("verbose:\n" + result.output)
        assert os.path.isfile("test.qrc")

        # Parse newly generated qrc file
        tree = etree.parse("test.qrc")
        root = tree.getroot()

        # Check qresources and their prefix attribute corresponding to
        # directories of the first level of resources folder
        first_dirs = [
            "/" + d for d in os.listdir(abs_res_folder)
            if os.path.isdir(os.path.join(abs_res_folder, d))
        ]
        first_dirs.append("/")

        for qresource in root.iter(tag="qresource"):
            assert qresource.attrib.get("prefix") in first_dirs
            directory = first_dirs.pop(
                first_dirs.index(qresource.attrib.get("prefix"))
            )

            # Get all resources files contained in the current qresource
            res = [resource.text for resource in qresource.iter(tag="file")]

            # Special case for root directory to not get into sub directories
            if directory == "/":
                resources = [
                    os.path.join(rel_res_folder, r)
                    for r in os.listdir(abs_res_folder)
                    if os.path.isfile(os.path.join(abs_res_folder, r))
                ]

                for resource in resources:
                    assert resource in res

                continue

            # Search if resource files have been recorded correctly in other
            # directories
            for root, dirs, files in os.walk(rel_res_folder + directory):
                for file_path in files:
                    assert os.path.join(root, file_path) in res

        # Verify if all dirs have been checked
        assert first_dirs == []
