import os


def test_initial_config_file(config):
    assert config.cparser.sections() == ['project']
    assert config.cparser.get("project", "name") == "test0"
    assert config.cparser.get("project", "path") == os.getcwd()


def test_get_qrcs(config):
    config.cparser.add_section("res")
    config.cparser.add_section("test")

    assert config.get_qrcs() == ["res", "test"]
