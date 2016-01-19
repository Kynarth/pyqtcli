import os
import yaml

from pyqtcli import verbose as v
from pyqtcli.config import ProjectConfig


def test_config_with_default_args(capsys):
    cfg = ProjectConfig()
    out, err = capsys.readouterr()

    with open(ProjectConfig.NAME, 'r') as f:
        config = yaml.load(f)

    # Verify config file content
    assert config == {'project': 'test0', 'path': os.getcwd()}

    # Verify ProjectConfig attributes
    assert cfg.dir_path == os.getcwd()
    assert cfg.path == os.path.join(os.getcwd(), ProjectConfig.NAME)
    assert cfg.name == "test0"

    # Check if the generation of the config file displays the correct message
    assert out.rstrip() == v.info(
        "The project named: 'test0' was initialized in {}".format(os.getcwd())
    )


def test_config_with_path_and_message_args(capsys):
    os.mkdir("config")
    config_dir = os.path.join(os.getcwd(), "config")
    config_path = os.path.join(config_dir, ProjectConfig.NAME)

    cfg = ProjectConfig("config", "I'm a test message")
    out, err = capsys.readouterr()

    with open(config_path, 'r') as f:
        config = yaml.load(f)

    # Verify config file content
    assert config == {'project': 'config', 'path': config_dir}

    # Verify ProjectConfig attributes
    assert cfg.dir_path == config_dir
    assert cfg.path == config_path
    assert cfg.name == "config"

    # Check if the generation of the config file displays the correct message
    assert out.rstrip() == v.info("I'm a test message")


def test_retrieving_existent_config_file(capsys):
    ProjectConfig()

    config_dir = os.getcwd()
    os.mkdir("sub_dir")
    os.chdir("sub_dir")
    config_path = os.path.join(config_dir, ProjectConfig.NAME)

    cfg = ProjectConfig()
    out, err = capsys.readouterr()

    with open(config_path, 'r') as f:
        config = yaml.load(f)

    # Verify config file content
    assert config == {'project': 'test0', 'path': config_dir}

    # Verify ProjectConfig attributes
    assert cfg.dir_path == config_dir
    assert cfg.path == config_path
    assert cfg.name == "test0"

    # Check if the generation of the config file displays the correct message
    assert out.rstrip() == v.info(
        "The project named: 'test0' was initialized in {}".format(config_dir)
    )
