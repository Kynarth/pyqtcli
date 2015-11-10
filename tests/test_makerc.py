import os

from textwrap import dedent
from click.testing import CliRunner

from pyqtcli.cli import pyqtcli

# Working directory to test files one level upper and still remain in
# the isolated file system
TEST_DIR = "test_dir"

QRC_DIR_1 = "qrc_test"          # Directory one level downer
QRC_DIR_2 = "../qrc_test_2"     # Directory one level higher

# Temporary qrc files to parse
QRC_FILE_1 = "res.qrc"
QRC_FILE_1_BIS = "res_bis.qrc"
QRC_FILE_2 = os.path.join(QRC_DIR_1, "res2.qrc")
QRC_FILE_3 = os.path.join(QRC_DIR_2, "res3.qrc")

# Fake text files for qrc files
TXT_FILE_1 = "test_file.txt"
TXT_FILE_2 = os.path.join(QRC_DIR_1, "test_file.txt")
TXT_FILE_3 = os.path.join(QRC_DIR_2, "test_file.txt")

# Expected result
RESULT1 = "res_rc.py"
RESULT1_BIS = "res_bis_rc.py"
RESULT2 = os.path.join(QRC_DIR_1, "res2_rc.py")
RESULT3 = os.path.join(QRC_DIR_2, "res3_rc.py")

# QRC test file model
QRC = """\
<RCC>
    <qresource prefix="/">
        <file>test_file.txt</file>
    </qresource>
</RCC>
"""


def test_makerc_with_on_file():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create tmp qrc test file
        open(TXT_FILE_1, 'a').close()

        with open(QRC_FILE_1, 'w') as f:
            f.write(dedent(QRC))

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", QRC_FILE_1]
        )

        print("\n===================== Test with one file ====================")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(RESULT1)


def test_makerc_with_two_files_in_same_directory():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create tmp qrc test files in same directory
        open(TXT_FILE_1, 'a').close()

        with open(QRC_FILE_1, 'w') as f:
            f.write(dedent(QRC))

        with open(QRC_FILE_1_BIS, 'w') as f:
            f.write(dedent(QRC))

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", QRC_FILE_1, QRC_FILE_1_BIS]
        )

        print("\n============== Test with two files on same dir ==============")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(RESULT1)
        assert os.path.isfile(RESULT1_BIS)


def test_makerc_with_3_files_in_different_dirs():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create dir to test qrc file in upper levels
        os.mkdir(TEST_DIR)
        os.chdir(TEST_DIR)

        # Create tmp qrc test files
        os.mkdir(QRC_DIR_1)
        os.mkdir(QRC_DIR_2)

        open(TXT_FILE_1, 'a').close()
        open(TXT_FILE_2, 'a').close()
        open(TXT_FILE_3, 'a').close()

        with open(QRC_FILE_1, 'w') as f:
            f.write(dedent(QRC))

        with open(QRC_FILE_2, 'w') as f:
            f.write(dedent(QRC))

        with open(QRC_FILE_3, 'w') as f:
            f.write(dedent(QRC))

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", QRC_FILE_1, QRC_FILE_2, QRC_FILE_3]
        )

        print("\n============ Test with 3 files on different dirs ============")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(RESULT1)
        assert os.path.isfile(RESULT2)
        assert os.path.isfile(RESULT3)


def test_makerc_recursive_option():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create tmp qrc test files in two directories
        os.mkdir(QRC_DIR_1)
        open(TXT_FILE_1, 'a').close()
        open(TXT_FILE_2, 'a').close()

        with open(QRC_FILE_1, 'w') as f:
            f.write(dedent(QRC))

        with open(QRC_FILE_2, 'w') as f:
            f.write(dedent(QRC))

        # Launch makerc command
        result = runner.invoke(
            pyqtcli, ["makerc", "-v", "-r"]
        )

        print("\n================== Test recursive option ====================")
        print("Exit code:", result.exit_code)
        print("Verbose:\n" + result.output)

        assert os.path.isfile(RESULT1)
        assert os.path.isfile(RESULT2)
