from lxml import etree
from pyqtcli.cli import pyqtcli
from click.testing import CliRunner


def test_addqres(config, resources):
    runner = CliRunner()

    # Generate a qrc file named res and update config file
    runner.invoke(pyqtcli, ["new"])

    # test addqres with default option
    result = runner.invoke(pyqtcli, ["addqres", "res.qrc", "resources"])
    assert result.exit_code == 0

    # Parse qrc file
    tree = etree.parse("res.qrc")
    root = tree.getroot()

    # Check qresource has been added
    qres_prefix = []  # Elements matching qresource with prefix = '/resources'
    for qresource in root.iter(tag="qresource"):
        if qresource.attrib.get("prefix") == "/resources":
            qres_prefix.append(qresource)
    assert len(qres_prefix) == 1

    # Check res_folder has beed added to dirs variable of config file
    config.read()
    assert config.cparser["res"].get("dirs") == "resources"
