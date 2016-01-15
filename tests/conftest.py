import os
import pytest

from pyqtcli.cli import pyqtcli
from click.testing import CliRunner
from pyqtcli.config import PyqtcliConfig


@pytest.fixture(autouse=True)
def tmp_test_dir(tmpdir_factory, request):
    """Fixture to create a dir for tests and remove it at the end.

    Args:
        tmpdir_factory: pytest's fixture to help generate temporary directories.
        request: pytest's fixture to access to the test context.
    """
    cwd = os.getcwd()
    tmp_dir = tmpdir_factory.mktemp("test")
    tmp_dir.chdir()

    def fin():
        os.chdir(cwd)
        tmp_dir.remove()
    request.addfinalizer(fin)


@pytest.fixture
def config():
    runner = CliRunner()
    runner.invoke(pyqtcli, ["init"])
    return PyqtcliConfig()


@pytest.fixture
def test_resources():
    """Generate a folder of resources to test qrc file."""
    # Create sub folders
    os.mkdir("resources")
    os.makedirs("resources/images/assets")
    os.makedirs("resources/images/toolbar")
    os.makedirs("resources/musics/solos/best")

    # Create fake files
    open('resources/file.txt', 'a').close()
    open('resources/images/banner.png', 'a').close()
    open('resources/images/assets/bg.bmp', 'a').close()
    open('resources/images/assets/fg.bmp', 'a').close()
    open('resources/images/assets/test.bmp', 'a').close()
    open('resources/images/toolbar/new.svg', 'a').close()
    open('resources/images/toolbar/quit.svg', 'a').close()
    open('resources/images/toolbar/search.svg', 'a').close()
    open('resources/musics/intro.ogg', 'a').close()
    open('resources/musics/outro.ogg', 'a').close()
    open('resources/musics/solos/solo1.mp3', 'a').close()
    open('resources/musics/solos/solo2.mp3', 'a').close()
    open('resources/musics/solos/best/best_solo1.mp3', 'a').close()
    open('resources/musics/solos/best/best_solo2.mp3', 'a').close()

    # Number of created files
    return 14
