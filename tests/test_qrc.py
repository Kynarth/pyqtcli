import os
import re
import pytest

from lxml import etree
from pyqtcli.qrc import read_qrc
from pyqtcli.test.qrc import QRCTestFile


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
    regex = re.compile(r"Error:.*")
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


def test_get_qresource():
    qrc = (
        QRCTestFile("res")
        .add_qresource().add_file("file.txt")
        .add_qresource("/images").add_file("logo.png")
        .build()
    )

    assert qrc.get_qresource("/images").attrib.get("prefix") == "/images"


def test_read_qrc():
    qrc = (
        QRCTestFile("res")
        .add_qresource().add_file("file.txt")
        .add_qresource("/images").add_file("logo.png")
        .build()
    )

    r_qrc = read_qrc("res.qrc")

    # check qrc content is the same
    assert etree.tostring(qrc._tree, pretty_print=True) == \
        etree.tostring(r_qrc._tree, pretty_print=True)

    # Check that the last qresource added is the same
    assert qrc._last_qresource.attrib == r_qrc._last_qresource.attrib

    # Check that the list of qresoource is identical
    for qres, r_qres in zip(qrc._qresources, r_qrc._qresources):
        assert qres.attrib == r_qres.attrib
