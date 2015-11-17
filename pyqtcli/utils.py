import os

from contextlib import contextmanager


@contextmanager
def cd(path):
    """
    Context manager to enter into directory and return to the previous one
    automatically consequently.

    Args:
        path (str): Path to directory to come into.

    """
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)
