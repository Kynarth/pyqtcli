import os
import pytest

from pyqtcli.utils import cd


def test_unique_cd(tmpdir):
    cwd = os.getcwd()
    dir_path = tmpdir.mkdir("sub").strpath

    with cd(dir_path):
        assert os.getcwd() == dir_path

    assert cwd == os.getcwd()


def test_nested_cd(tmpdir):
    cwd = os.getcwd()
    dir_path = tmpdir.mkdir("sub").strpath
    nested_path = tmpdir.mkdir("sub/nested").strpath

    with cd(dir_path):
        assert os.getcwd() == dir_path
        with cd(nested_path):
            assert os.getcwd() == nested_path

    assert cwd == os.getcwd()


def test_false_cd(tmpdir):
    cwd = os.getcwd()

    with pytest.raises(FileNotFoundError):
        with cd("azerty"):
            pass

    assert cwd == os.getcwd()
