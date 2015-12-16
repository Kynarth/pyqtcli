from lxml import etree
from click.testing import CliRunner

from pyqtcli.cli import pyqtcli
from pyqtcli.test.qrc import QRCTestFile


def test_makealias_with_on_file():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create false qrc files for testing
        qrc = (
            QRCTestFile("res")
            .add_qresource().add_file("file.txt").add_file("test.txt")
            .add_qresource("/images").add_file("images/icon.png").build()
        )

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makealias", "-v", qrc.path]
        )

        print("Verbose:\n" + result.output)

        assert result.exit_code == 0


def test_makealias_with_duplication():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create false qrc files for testing
        qrc = (
            QRCTestFile("res")
            .add_qresource("/").add_file("file.txt").add_file("test/file.txt")
            .build()
        )

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makealias", "-v", qrc.path]
        )

        print("Verbose:\n" + result.output)

        tree = etree.parse(qrc.path)
        root = tree.getroot()

        resources = [resource for resource in root.iter(tag="file")]

        assert resources[0].attrib.get("alias")
        assert resources[1].attrib.get("alias") == None


def test_makealias_recursive():
    runner = CliRunner()

    with runner.isolated_filesystem():
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
        result = runner.invoke(
            pyqtcli, ["makealias", "-v", "-r"]
        )

        print("Verbose:\n" + result.output)

        # Assert all qrc resources get their alias
        for qrc_file in qrcs:
            tree = etree.parse(qrc_file.path)
            root = tree.getroot()

            for resource in root.iter(tag="file"):
                assert resource.attrib.get("alias")
