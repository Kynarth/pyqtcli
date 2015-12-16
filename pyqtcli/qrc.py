"""This module enable user to generate qrc file for qt project."""

import os
import sys

from lxml import etree


class QRCFile():
    """Class generating qrc file.
    Attributes:
        name (str): File name of the new qrc file. Qrc extension is
            automatically added.
        path (optional[str]): Absolute ath to new qrc file.
        dir_path (str): Absolute path to the qrc file directory.
        _qresources (list[etree.SubElement]): List of qresources created.
        _last_qresource (etree.SubElement): Last qresource created.
        _root (etree.Element): Root element of qrc file.
        _tree (etree.ElementTree): Qrc tree with added qresources and resources.
    """

    def __init__(self, name, path="."):
        self.name = name if os.path.splitext(name)[1] else name + ".qrc"
        self.dir_path = os.path.abspath(path)
        self.path = os.path.join(self.dir_path, self.name)
        self._qresources = []
        self._last_qresource = None
        self._root = etree.Element("RCC")
        self._tree = etree.ElementTree(self._root)

    def add_qresource(self, prefix=None):
        """Create to the qresource subelement.
        Args:
            prefix (str[optional]): Prefix attribute like => "/"
                for qresource element.
        """
        # Check if given prefix does not already exist.
        for qresource in self._qresources:
            if qresource.get("prefix", None) == prefix:
                msg = (
                    "Error: Qresource with prefix: '{}' already exists."
                ).format(prefix)
                sys.exit(msg)

        # Create element
        if prefix is not None:
            self._last_qresource = etree.SubElement(
                self._root, "qresource", {"prefix": prefix}
            )
        else:
            self._last_qresource = etree.SubElement(self._root, "qresource")

        # Add created element to others
        self._qresources.append(self._last_qresource)

    def get_qresource(self, prefix):
        """Get qresource element corresponding to the passed prefix.

        Args:
            prefix (str): "Name of prefix" Ex: "/images"

        Returns:
            etree.Element: Corresponding qresource to prefix

        """
        for qresource in self._qresources:
            if qresource.attrib.get("prefix") == prefix:
                return qresource

        return None

    def add_file(self, resource, prefix=None):
        """Add a resource to a given prefix.
        Args:
            resource (str): Path to the resource.
            prefix (str): Prefix attribute like => "/" for qresource element.
        """
        # Create empty prefix qresource if user doesn't provide it yet
        if self._last_qresource is None:
            self.add_qresource()

        # Check if given prefix does exist
        if prefix:
            qresource_found = False
            for qresource in self._qresources:
                if qresource.get("prefix") == prefix:
                    self._last_qresource = qresource
                    qresource_found = True
                    break
            if not qresource_found:
                msg = (
                    "Error: Qresource with prefix: "
                    "'{}' does not exist."
                ).format(prefix)
                sys.exit(msg)

        # Add the resource to qresource element
        etree.SubElement(self._last_qresource, "file",).text = resource

    def build(self):
        """Generate qrc file in function avec path and name attribute."""
        # Create directories for qrc file if not exist
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)

        # Write qrc file
        with open(self.path, "w") as f:
            f.write(etree.tostring(
                self._tree, pretty_print=True).decode('utf-8')
            )


def read_qrc(qrc):
    """Parse a qrc file to return a QRCFile object.

    Args:
        qrc (str): Path to the qrc file.

    Returns:
        QRCFile: QRCFile represening passed qrc file.

    """
    path, name = os.path.split(qrc)
    qrcfile = QRCFile(name, path)

    qrcfile._tree = etree.parse(qrc)
    qrcfile._root = qrcfile._tree.getroot()

    for qresource in qrcfile._root.iter(tag="qresource"):
        qrcfile._qresource = qresource
        qrcfile._last_qresource = qresource

    return qrcfile


def fill_qresource(qrc, folder, prefix=None):
    """Fill a qrc with resources contained in the passed folder.

    Each file of resource folder will be record as <file> subelement of the
    corresponding qresource element (see prefix). The value of the subelement
    is the relative path between the resource within the folder and the
    qrc path.

    Args:
        qrc (QRCFile): A QRCFile object to add and fill qresource.
        folder (str): Path to the folder of resources to record.
    """
    for root, dirs, files in os.walk(folder):
        for resource in files:
            resource_path = os.path.join(root, resource)
            # Relative path between qrc file and the resource
            path = os.path.relpath(resource_path, qrc.dir_path)

            if prefix:
                qrc.add_file(path, prefix)
            else:
                qrc.add_file(path)
