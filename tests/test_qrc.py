import os
import pytest

from pyqtcli.qrc import QRCFile
from pyqtcli.qrc import read_qrc
from pyqtcli.qrc import get_prefix_update
from pyqtcli.qrc import fill_qresource
from pyqtcli.test.qrc import QRCTestFile
from pyqtcli.exception import QresourceError
from pyqtcli.exception import QRCFileError


def test_simple_qrc():
    qrc = QRCTestFile("res").add_qresource().add_file("file.txt").build()

    assert os.path.isfile(qrc.path)


def test_complex_qrc():
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


def test_add_qresource():
    qrc = QRCTestFile("res.qrc").add_qresource("/").build()

    qrc.get_qresource("/")


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
    assert qresource not in qrc.qresources

    with pytest.raises(QresourceError) as e:
        qrc.get_qresource("/images")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'/images\' prefix")


def test_add_file():
    qrc = QRCTestFile("res.qrc").add_qresource().add_file("test.txt").build()

    assert qrc.get_file("test.txt", "/").text == "test.txt"


def test_add_file_to_nonexistent_qresource():
    with pytest.raises(QresourceError) as e:
        qrc = QRCFile("res.qrc")
        qrc.add_file("test.txt", '/')
        qrc.build()
    assert str(e.value) == ("Error: No <qresource> node corresponding to '/' "
                            "prefix")


def test_get_file():
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("test.txt").add_file("fg.bpm")
        .add_qresource("/test").add_file("file.txt").add_file("logo.png")
        .build()
    )
    assert qrc.get_file("logo.png", "/test").text == "logo.png"


def test_get_wrong_file():
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("test.txt").add_file("fg.bpm")
        .add_qresource("/test").add_file("file.txt").add_file("logo.png")
        .build()
    )

    with pytest.raises(QresourceError) as e:
        qrc.get_file("fg.png", "/test")
    assert str(e.value) == (
        "Error: No <file> child corresponding to \'fg.png\' in "
        "qresource \'/test\'")


def test_remove_resource():
    qrc = QRCTestFile("res.qrc").add_qresource().add_file("test.txt").build()
    assert qrc.remove_resource("test.txt", "/").text == "test.txt"

    with pytest.raises(QresourceError) as e:
        qrc.get_file("test.txt", "/")
    assert str(e.value) == ("Error: No <file> child corresponding to "
                            "'test.txt' in qresource \'/\'")


def test_remove_nonexistent_resource():
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("test.txt")
        .add_qresource("/test").add_file("file.txt")
        .build()
    )
    with pytest.raises(QresourceError) as e:
        qrc.remove_resource("file.txt", "/")
    assert str(e.value) == ("Error: No <file> child corresponding to "
                            "'file.txt' in qresource \'/\'")


def test_remove_file():
    qrc = QRCTestFile("res.qrc").add_qresource().add_file("test.txt").build()
    res = qrc.get_file("test.txt", "/")
    assert qrc.remove_file(res, "/").text == "test.txt"

    with pytest.raises(QresourceError) as e:
        qrc.get_file("test.txt", "/")
    assert str(e.value) == ("Error: No <file> child corresponding to "
                            "'test.txt' in qresource \'/\'")


def test_remove_nonexistent_file_in_qresource():
    qrc = (
        QRCTestFile("res.qrc")
        .add_qresource().add_file("test.txt")
        .add_qresource("/test").add_file("file.txt")
        .build()
    )
    res = qrc.get_file("file.txt", "/test")
    with pytest.raises(ValueError) as e:
        qrc.remove_file(res, "/")
    assert str(e.value) == "Element is not a child of this node."


def test_list_resources():
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

    # Test for a nonexistent qresource
    with pytest.raises(QresourceError) as e:
        qrc.list_resources("/test")
    assert str(e.value) == (
        "Error: No <qresource> node corresponding to \'/test\' prefix")


def test_list_files():
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
    assert qrc.list_files() == [r_file for r_file in qrc.root.iter(tag="file")]

    # Test for a nonexistent qresource
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

    # Check that the list of qresource is identical
    for qres, r_qres in zip(qrc.qresources, r_qrc.qresources):
        assert qres.attrib == r_qres.attrib


def test_read_qrc_on_nonexistent_qrc():
    with pytest.raises(QRCFileError) as e:
        read_qrc("res.qrc")
    assert str(e.value) == "Error: Qrc file \'res.qrc\' does not exist."


def test_prefix_update():
    # Simple path
    assert get_prefix_update("resources") == "/"
    assert get_prefix_update("resources/") == "/"

    # complex path
    assert get_prefix_update("resources/images/logo") == "/logo"

    # path finishing with "/"
    assert get_prefix_update("resources/") == "/"
    assert get_prefix_update("resources/images/logo/") == "/logo"


# noinspection PyUnusedLocal
def test_fill_qresource_with_root_prefix(config, test_resources):
    # Test with prefix "/"
    qrc = QRCTestFile("res.qrc").add_qresource().add_qresource("/images")
    fill_qresource(qrc, "resources", "/")

    assert qrc.list_resources("/") == ["resources/file.txt"]
    assert qrc.list_resources("/images") == []

    # Check if resources are relative paths from project directory
    for resource in qrc.list_resources("/"):
        assert resource.startswith("resources/")


# noinspection PyUnusedLocal
def test_fill_qresource_with_any_prefix(config, test_resources):
    # Test with prefix "/images"
    qrc = QRCTestFile("res.qrc").add_qresource().add_qresource("/images")
    fill_qresource(qrc, "resources/images", "/images")

    assert qrc.list_resources("/") == []
    assert sorted(qrc.list_resources("/images")) != sorted([
           "resources/musics/outro.ogg",
           "resources/musics/intro.ogg",
           "resources/musics/solos/solo2.mp3",
           "resources/musics/solos/solo1.mp3",
           "resources/musics/solos/best/best_solo2.mp3",
           "resources/musics/solos/best/best_solo1.mp3"
    ])

    # Check if resources are relative paths from project directory
    for resource in qrc.list_resources("/images"):
        assert resource.startswith("resources/images")


# noinspection PyUnusedLocal
def test_fill_qresource_with_two_prefixes(config, test_resources):
    qrc = QRCTestFile("res.qrc").add_qresource().add_qresource("/images")
    fill_qresource(qrc, "resources", "/")
    fill_qresource(qrc, "resources/images", "/images")

    assert qrc.list_resources("/") == ["resources/file.txt"]
    assert sorted(qrc.list_resources("/images")) != sorted([
           "resources/musics/outro.ogg",
           "resources/musics/intro.ogg",
           "resources/musics/solos/solo2.mp3",
           "resources/musics/solos/solo1.mp3",
           "resources/musics/solos/best/best_solo2.mp3",
           "resources/musics/solos/best/best_solo1.mp3"
    ])

    # Check if resources are relative paths from project directory
    for resource in qrc.list_resources("/"):
        assert resource.startswith("resources/")

    for resource in qrc.list_resources("/images"):
        assert resource.startswith("resources/images")
