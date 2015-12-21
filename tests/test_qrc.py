import os
import pytest

from pyqtcli.qrc import read_qrc
from pyqtcli.test.qrc import QRCTestFile
from pyqtcli.exception import QresourceError
from pyqtcli.exception import QRCFileError


def test_simple_qrc():
    qrc = QRCTestFile("res").add_qresource().add_file("file.txt").build()

    assert os.path.isfile(qrc.path)


def test_complexe_qrc():
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
    with pytest.raises(QresourceError) as e:
        (
            QRCTestFile("res")
            .add_qresource().add_file("file.txt")
            .add_qresource("/images").add_file("images/test.txt")
            .add_file("test.txt", "prefix")
            .build()
        )
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'prefix\' prefix"
    )


def test_duplication_of_qresource():
    with pytest.raises(QresourceError) as e:
        (
            QRCTestFile("res")
            .add_qresource().add_file("file.txt")
            .add_qresource().add_file("images/test.txt")
            .build()
        )
    assert str(e.value) == "Error: qresource with prefix: \'/\' already exists"


def test_get_qresource():
    qrc = (
        QRCTestFile("res")
        .add_qresource().add_file("file.txt")
        .add_qresource("/images").add_file("logo.png")
        .build()
    )

    assert qrc.get_qresource("/images").attrib.get("prefix") == "/images"

    with pytest.raises(QresourceError) as e:
        qrc.get_qresource("/test")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'/test\' prefix")


def test_remove_qresource():
    qrc = (
        QRCTestFile("res")
        .add_qresource().add_file("file.txt")
        .add_qresource("/images").add_file("logo.png")
        .build()
    )

    qresource = qrc.remove_qresource("/images")
    assert qresource not in qrc._qresources

    with pytest.raises(QresourceError) as e:
        qrc.get_qresource("/images")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'/images\' prefix")


def test_list_resources(config):
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("test.txt").add_file("file.txt")
        .add_qresource("/images").add_file("images/logo.png")
        .add_file("images/fg.bmp")
        .build()
    )

    # Test list of resources for each qresources
    assert sorted(qrc.list_resources("/")) == sorted(["test.txt", "file.txt"])
    assert sorted(qrc.list_resources("/images")) == sorted(
        ["images/logo.png", "images/fg.bmp"])

    # Test list of resources for all qresources
    assert sorted(qrc.list_resources()) == sorted(
        ["test.txt", "file.txt", "images/logo.png", "images/fg.bmp"]
    )

    # Test for a nonexistant qresource
    with pytest.raises(QresourceError) as e:
        qrc.list_resources("/test")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'/test\' prefix")


def test_list_files(config):
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("test.txt").add_file("file.txt")
        .add_qresource("/images").add_file("images/logo.png")
        .add_file("images/fg.bmp")
        .build()
    )

    # Test list of files for each qresources
    root_qresource = qrc.get_qresource("/")
    root_files = [r_file for r_file in root_qresource.iter(tag='file')]
    assert qrc.list_files("/") == root_files

    images_qresource = qrc.get_qresource("/images")
    images_files = [r_file for r_file in images_qresource.iter(tag='file')]
    assert qrc.list_files("/images") == images_files

    # Test list of files for all qresources
    assert qrc.list_files() == [r_file for r_file in qrc._root.iter(tag="file")]

    # Test for a nonexistant qresource
    with pytest.raises(QresourceError) as e:
        qrc.list_files("/test")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'/test\' prefix")


def test_read_qrc():
    qrc = (
        QRCTestFile("res")
        .add_qresource().add_file("file.txt")
        .add_qresource("/images").add_file("logo.png").add_file("fg.bmp")
        .build()
    )

    r_qrc = read_qrc("res.qrc")

    # check qrc content is the same
    assert str(qrc) == str(r_qrc)

    # Check that the list of qresoource is identical
    for qres, r_qres in zip(qrc._qresources, r_qrc._qresources):
        assert qres.attrib == r_qres.attrib


def test_read_qrc_on_nonexistant_qrc():
    with pytest.raises(QRCFileError) as e:
        read_qrc("res.qrc")
    assert str(e.value) == "Error: Qrc file \'res.qrc\' does not exist."
