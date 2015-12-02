import os
import pytest

from pyqtcli.config import PyqtcliConfig


@pytest.fixture(autouse=True)
def tmp_test_dir(tmpdir_factory, request):
    """Fixture to create a dir for tests and remove it at the end."""
    cwd = os.getcwd()
    tmp_dir = tmpdir_factory.mktemp("test")
    tmp_dir.chdir()

    def fin():
        os.chdir(cwd)
        tmp_dir.remove()
    request.addfinalizer(fin)


@pytest.fixture
def config():
    return PyqtcliConfig()
