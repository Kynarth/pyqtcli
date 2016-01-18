import os
import pytest


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
