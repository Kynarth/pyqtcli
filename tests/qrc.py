import os
import sys

from lxml import etree

from pyqtcli.qrc import chain
from pyqtcli.qrc import QRCFile
from pyqtcli.qrc import GenerativeBase


class TestQRCFile(QRCFile, GenerativeBase):
    """Generate a qrc file for tests with false resource directories and files.

    Attributes:
        name (str): File name of the new qrc file.
        path (optional[str]): Path to new qrc file dir.
        _qresources (list[etree.SubElement]): List of qresources created.
        _last_qresource (etree.SubElement): Last qresource created.


    Example:
        >>>(
        ...    TestQRCFile("test")
        ...    .add_qresource("/")
        ...    .add_file("test.txt")
        ...    .add_file("test1.txt")
        ...    .add_qresource("/images")
        ...    .add_file("img.png")
        ...    .build()
        ...)

    """

    def __init__(self, name, path="."):
        super(TestQRCFile, self).__init__(name, path)

    @chain
    def add_qresource(self, prefix):
        """Create qresource subelement with prefix attribute.

        Args:
            prefix (str): Prefix attribute like => "/" for qresource element.

        """
        super().add_qresource(prefix)

        # Create element
        self._last_qresource = etree.SubElement(
            self._root, "qresource", {"prefix": prefix}
        )

        # Change prefix for "" if "/" is provided
        if prefix.startswith("/"):
            prefix = ""

        # Create dir for given prefix
        dir_path = os.path.join(os.path.dirname(self.path), prefix)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

    @chain
    def add_file(self, resource):
        """
        Add a file to the last added qresource and create its file in a
        dir corresponding to the qresource's prefix attribute.

        Args:
            resource (str): Path to the resource.

        """
        super().add_file(resource)

        # Change prefix for "" if "/" is provided
        path = self._last_qresource.get("prefix")
        if path.startswith("/"):
            path = ""

        # Create the resource
        file_path = os.path.join(os.path.dirname(self.path), path, resource)
        if not os.path.isfile(file_path):
            open(file_path, 'a').close()
        else:
            print("Error: the file: {} already exists.".format(file_path))
            sys.exit(1)
