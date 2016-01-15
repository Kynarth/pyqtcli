import os
import subprocess

from pyqtcli import verbose as v


# Error message send by pyrcc5 when qrc file doesn't contain resources
NO_QRESOURCE = b"No resources in resource description.\n"
INVALID_QRC = b"pyrcc5 Parse Error:"


def generate_rc(qrc_files, verbose):
    """Generate python module to access qrc resources via pyrcc5 tool.

    Args:
        qrc_files (list or tuple): A tuple containing all paths to qrc files
            to process.
        verbose (bool): True if the user pass '-v' or '--verbose' option
            to see what's happening.

    Examples:
        This example will create two files: res_rc.py and qtc/another_res_rc.py

        >>> generate_rc(["res.qrc", "qrc/another_res.qrc"])

    """
    for qrc_file in qrc_files:
        # rc file name
        result_file = os.path.splitext(qrc_file)[0] + "_rc.py"

        # generate rc file corresponding to qrc file
        result = subprocess.run(["pyrcc5", qrc_file, "-o", result_file],
                                stderr=subprocess.PIPE)

        # Case where qrc has no more resources -> can't generate rc file
        if result.stderr == NO_QRESOURCE:
            v.warning(
                ("{} has no more resources and cannot generates its "
                 "corresponding rc file.").format(qrc_file))
            continue
        elif result.stderr.startswith(INVALID_QRC):
            v.warning("Qrc file: \'{}\' is not valid.".format(qrc_file))
            continue
        elif result.stderr:
            v.warning(result.stderr.decode("utf-8"))
            continue

        v.info("Python qrc file '{}' created.".format(result_file), verbose)
