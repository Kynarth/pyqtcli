import os


def recursive_process(cur_dir="."):
    """Search all qrc files recursively from given directory for process.

    Args:
        cur_dir (str): Directory from which we must seek for qrc files.

    Example:
        In case where we have "res.qrc" and "qrc/another.qrc":

        >>> recursive_process()
        >>> ["res.qrc", "qrc/another.qrc"]

    """
    qrc_files = []  # Contains found qrc files

    for root, dirs, files in os.walk(cur_dir):
        for name in files:
            if name.endswith('.qrc'):
                qrc_files.append(os.path.join(root, name))

    return tuple(qrc_files)
