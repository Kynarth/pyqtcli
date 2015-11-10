import os
import click
import subprocess


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


def process_qrc_files(qrc_files, verbose):
    """Generate python module to access qrc ressources via pyrcc5 tool.

    Args:
        qrc_files (tuple): A tuple containing all paths to qrc files to process.
        verbose (bool): True if the user pass '-v' or '--verbose' option
            to see what's happening.

    Examples:
        This example will create two files: res_rc.py and qtc/another_res_rc.py

        >>> process_qrc_files("res.qrc", "qrc/another_res.qrc)

    """
    for qrc_file in qrc_files:
        # Get absolute path
        qrc_file = os.path.abspath(qrc_file)

        result_file = os.path.splitext(qrc_file)[0] + "_rc.py"
        # if not subprocess.call(["pyrcc5", qrc_file, "-o", result_file]):
        if subprocess.call(["pyrcc5", qrc_file, "-o", result_file]):
            # Let pyrcc5 give his error message
            continue

        # Manage -v --verbose option
        if verbose:
            click.echo("Python qrc file '{}' created.".format(result_file))
