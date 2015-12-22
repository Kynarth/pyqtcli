"""This module enable user to generate qrc file for qt project."""

import os

from lxml import etree
from pyqtcli.exception import QresourceError
from pyqtcli.exception import QRCFileError


class QRCFile():
    """Class generating qrc file.

    Attributes:
        name (str): File name of the new qrc file. Qrc extension is
            automatically added.
        path (optional[str]): Absolute ath to new qrc file.
        dir_path (str): Absolute path to the qrc file directory.
        _qresources (list[etree.SubElement]): List of qresources created.
        _root (etree.Element): Root element of qrc file.
        _tree (etree.ElementTree): Qrc tree with added qresources and resources.
    """

    def __init__(self, name, path="."):
        self.name = name if os.path.splitext(name)[1] else name + ".qrc"
        self.dir_path = os.path.abspath(path)
        self.path = os.path.join(self.dir_path, self.name)
        self._qresources = []
        self._root = etree.Element("RCC")
        self._tree = etree.ElementTree(self._root)

    def add_qresource(self, prefix=None):
        """Create to the qresource subelement.

        Args:
            prefix (str[optional]): Prefix attribute like => "/"
                for qresource element.

        Raises:
            QresourceError: Raised when the passed prefix corresponds
                to an existing <qresource> node in the qrc file.

        """
        # Get qresource node corresponding to the passed prefix
        try:
            qresource = self.get_qresource(prefix)
        except QresourceError:
            qresource = None

        # If a qresource is found -> duplication and so raise error
        if qresource is not None:
            raise QresourceError((
                "Error: qresource with prefix: \'{}\' already "
                "exists").format(prefix)
            )

        # Create element
        if prefix is not None:
            qresource = etree.SubElement(
                self._root, "qresource", {"prefix": prefix})
        else:
            qresource = etree.SubElement(self._root, "qresource")

        # Add created element to others
        self._qresources.append(qresource)

    def remove_qresource(self, prefix):
        """Remove a qresource and its children from qrc file.

        Args:
            prefix (str): "Name of prefix" Ex: "/images"

        Returns:
            lxml.etree._Element: Returns removed qresource.

        Raises:
            QresourceError: Raised when the passed prefix doesn't correspond
                to any existing <qresource> node in the qrc file.

        """
        qresource = self.get_qresource(prefix)
        self._qresources.remove(qresource)
        qresource.getparent().remove(qresource)
        return qresource

    def get_qresource(self, prefix):
        """Get qresource element corresponding to the passed prefix.

        Args:
            prefix (str): "Name of prefix" Ex: "/images"

        Returns:
            etree.Element: Corresponding qresource to prefix

        Raises:
            QresourceError: Raised when the passed prefix doesn't correspond
                to any existing <qresource> node in the qrc file.

        """
        for qresource in self._qresources:
            if qresource.attrib.get("prefix", None) == prefix:
                return qresource

        raise QresourceError(
            "Error: No <qresource> node corresponding to \'{}\' prefix".format(
                prefix)
        )

    def add_file(self, resource, prefix):
        """Add a resource to a given prefix.

        Args:
            resource (str): Path to the resource.
            prefix (str): Prefix attribute like => "/" for qresource element.

        Raises:
            QresourceError: Raised when the passed prefix doesn't correspond
                to any existing <qresource> node in the qrc file.

        """
        # Get qresource node corresponding to the passed prefix
        qresource = self.get_qresource(prefix)

        # Add the resource to qresource element
        etree.SubElement(qresource, "file",).text = resource

    def list_resources(self, prefix=None):
        """
        List all <file> subelements text from the qresource containing passed
        prefix attribute.

        Args:
            prefix (str): Prefix attribute like => "/" for qresource element.

        Returns:
            list: A list of all resources path contained in qresource
                designated by the `prefix` or all qrc's resources.

        Raises:
            QresourceError: Raised when the passed prefix doesn't correspond
                to any existing <qresource> node in the qrc file.

        """
        if prefix:
            qresource = self.get_qresource(prefix)
            return [resource.text for resource in qresource.iter(tag="file")]
        else:
            resources = []
            for qresource in self._qresources:
                for resource in qresource.iter(tag="file"):
                    resources.append(resource.text)
            return resources

    def list_files(self, prefix=None):
        """
        List all <file> subelements from the qresource containing passed
        prefix attribute.

        Args:
            prefix (str): Prefix attribute like => "/" for qresource element.

        Returns:
            list: A list of all <file> subelement contained in qresource
                designated by the `prefix` or all qrc's <file> if no prefix.

        Raises:
            QresourceError: Raised when the passed prefix doesn't correspond
                to any existing <qresource> node in the qrc file.

        """
        if prefix:
            qresource = self.get_qresource(prefix)
            return [resource for resource in qresource.iter(tag="file")]
        else:
            files = []
            for qresource in self._qresources:
                for resource in qresource.iter(tag="file"):
                    files.append(resource)
            return files

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

    def __str__(self):
        return etree.tostring(self._root, pretty_print=True).decode("utf-8")


def read_qrc(qrc):
    """Parse a qrc file to return a QRCFile object.

    Args:
        qrc (str): Path to the qrc file.

    Returns:
        QRCFile: QRCFile represening passed qrc file.

    Raised:
        QRCFileError: Raised when passed qrc file does not exist.

    """
    if not os.path.isfile(qrc):
        raise QRCFileError("Error: Qrc file \'{}\' does not exist.".format(qrc))

    path, name = os.path.split(qrc)
    qrcfile = QRCFile(name, path)

    parser = etree.XMLParser(remove_blank_text=True)
    qrcfile._tree = etree.parse(qrc, parser)
    qrcfile._root = qrcfile._tree.getroot()

    for qresource in qrcfile._root.iter(tag="qresource"):
        qrcfile._qresources.append(qresource)

    return qrcfile


def fill_qresource(qrc, folder, prefix):
    """Fill a qrc with resources contained in the passed folder.

    Each file of resource folder will be record as <file> subelement of the
    corresponding qresource element (see prefix). The value of the subelement
    is the relative path between the resource within the folder and the
    qrc path.

    Args:
        qrc (QRCFile): A QRCFile object to add and fill qresource.
        folder (str): Path to the folder of resources to record.
        prefix (str): <qresource>'s prefix in which add the <file>.

    """
    for root, dirs, files in os.walk(folder):
        for resource in files:
            resource_path = os.path.join(root, resource)

            # Relative path between qrc file and the resource
            path = os.path.relpath(resource_path, qrc.dir_path)

            qrc.add_file(path, prefix)


def generate_qrc(qrc, res_folder, build=True):
    """Generate qrc file with provided folder of resources. The root of the
    resources folder correspond to qresource with "/" prefix. Resources that are
    not in folders will be recorded a <file> subelement to "/" qresource.
    For each directory present in the resources folder a qresource with
    "/" + directory's name as prefix will be created. In each of these
    directory, files are recursively recorded in corresponding qresource.

    Args:
        qrc_name (QRCFile): A newly created QRCFile.
        res_folder (str): Path to the folder of resources.
        build (bool): If True `QRCFile` object is save into qrc file.

    """
    # Loop over the folder of resources
    for root, dirs, files in os.walk(res_folder):
        if root == res_folder:
            qrc.add_qresource("/")
            # Directories in the first level will serve as qresource
            for directory in dirs:
                qrc.add_qresource("/" + directory)

        # Record all resources recursively
        for resource in files:
            try:
                prefix = "/" + root.replace(res_folder, "").split("/")[1]
            except IndexError:
                prefix = "/"
            qrc.add_file(os.path.join(root, resource), prefix)

    # Write qrc file
    if build:
        qrc.build()
