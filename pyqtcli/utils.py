"""Module with utils functions."""

import os


def recursive_file_search(ext, directory="."):
    """Search recursively files matching passed extension from given directory.

    Args:
        ext (str): File extension to search for.
        directory (str[optional]): Directory from which we must seek for files.

    Returns:
        list: A list relative paths to matching files.

    Raises:
        FileNotFoundError: if `directory` isn't a correct directory

    Example:
        In case where we have "res.qrc" and "qrc/another.qrc":

        >>> recursive_file_search("qrc")
        >>> ["res.qrc", "qrc/another.qrc"]

    """
    if not os.path.isdir(directory):
        raise FileNotFoundError("No such directory: '{}'".format(directory))

    found_files = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith('.' + ext):
                found_files.append(os.path.join(root, name))

    return found_files
