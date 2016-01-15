"""This module enable user to generate qrc file for qt project."""

import os

from lxml import etree

from pyqtcli.config import find_project_config
from pyqtcli.exception import QresourceError
from pyqtcli.exception import QRCFileError


class QRCFile:
    """Class generating qrc file.

    Attributes:
        name (str): File name of the new qrc file. Qrc extension is
            automatically added.
        path (Optional[str]): Absolute ath to new qrc file.
        dir_path (str): Absolute path to the qrc file directory.
        _qresources (list[:class:`etree.SubElement`]): List of qresources
            created.
        _root (:class:`etree.Element`): Root element of qrc file.
        _tree (:class:`etree.ElementTree`): Qrc tree with added qresources and
            resources.

    """
    def __init__(self, name, path="."):
        self.name = name if os.path.splitext(name)[1] else name + ".qrc"
        self.dir_path = os.path.abspath(path)
        self.path = os.path.join(self.dir_path, self.name)
        self._qresources = []
        self._root = etree.Element("RCC")
        self._tree = etree.ElementTree(self._root)

    def add_qresource(self, prefix=None, folder=None):
        """Create to the qresource subelement.

        Create a qresource node in the qrc file. If `folder` is provided,
        in addition to create qresource node, this method will record all
        resources present in `folder` as <file> subelement.

        Args:
            prefix (Optional[str]): Prefix attribute like => "/"
                for qresource element.
            folder (Optional[str]): Path to the folder corresponding to the
                qresource.

        Raises:
            :class:`QresourceError`: Raised when the passed prefix corresponds
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

        if folder:
            fill_qresource(self, folder, prefix)

        # Add created element to others
        self._qresources.append(qresource)

    def remove_qresource(self, prefix):
        """Remove a qresource and its children from qrc file.

        Args:
            prefix (str): "Name of prefix" Ex: "/images"

        Returns:
            :class:`etree.Element`: Returns removed qresource.

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
            :class:`etree.Element`: Corresponding qresource to prefix

        Raises:
            :class:`QresourceError`: Raised when the passed prefix doesn't
                correspond to any existing <qresource> node in the qrc file.

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
            :class:`QresourceError`: Raised when the passed prefix doesn't
                correspond to any existing <qresource> node in the qrc file.

        """
        # Get qresource node corresponding to the passed prefix
        qresource = self.get_qresource(prefix)

        # Add the resource to qresource element
        etree.SubElement(qresource, "file",).text = resource

    def remove_resource(self, resource, prefix):
        """
        Remove a <file> node matching `resource` from a qresource
        identify by a prefix.

        Args:
            resource (str): Path to the resource
            prefix (str): Prefix attribute like => "/" for qresource element.

        Returns:
            :class:`etree.Element`: Returns the removed <file> element.

        Raises:
            :class:`QresourceError`: Raised when
                - `prefix` doesn't correspond to any existing <qresource>
                    node in the qrc file.
                - No <file> element correspond to `resource`.

        """
        # Get qresource node corresponding to the passed prefix
        qresource = self.get_qresource(prefix)

        # Get <file> element corresponding to resource
        res = self.get_file(resource, prefix)

        # Remove the resource from qresource element
        qresource.remove(res)

        return res

    def remove_file(self, resource, prefix):
        """
        Remove a <file> node matching `resource` from a qresource
        identify by a prefix.

        Args:
            resource (lxml.etree.Element): <file> to remove
            prefix (str): Prefix attribute like => "/" for qresource element.

        Returns:
            :class:`etree.Element`: Returns the removed <file> element.

        Raises:
            :class:`QresourceError`: Raised when the passed prefix doesn't
                correspond to any existing <qresource> node in the qrc file.
            :class:`ValueError`: Raised when the resource isn't child of the
                qresource corresponding to given prefix.

        """
        # Get qresource node corresponding to the passed prefix
        qresource = self.get_qresource(prefix)

        # Remove the resource from qresource element
        qresource.remove(resource)

        return resource

    def get_file(self, resource, prefix):
        """Remove a resource from a qresource identify by a prefix.

        Args:
            resource (str): Path to resource
            prefix (str): Prefix attribute like => "/" for qresource element.

        Returns:
            :class:`etree.Element`: Return the corresponding <file> element to
                `resource`.

        Raises:
            :class:`QresourceError`: Raised when
                - `prefix` doesn't correspond to any existing <qresource>
                    node in the qrc file.
                - No <file> element correspond to `resource`.

        """
        # Get qresource node corresponding to the passed prefix
        qresource = self.get_qresource(prefix)

        for res in qresource.iter(tag="file"):
            if res.text == resource:
                return res

        raise QresourceError(
            ("Error: No <file> child corresponding to \'{}\' in "
             "qresource \'{}\'").format(resource, prefix))

    def list_resources(self, prefix=None):
        """
        List all <file> subelements text from the qresource containing passed
        prefix attribute.

        Args:
            prefix (Optional[str]): Prefix attribute like => "/" for qresource.

        Returns:
            list: A list of all resources path contained in qresource
                designated by the `prefix` or all qrc's resources.

        Raises:
            :class:`QresourceError`: Raised when the passed prefix doesn't
                correspond to any existing <qresource> node in the qrc file.

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
            prefix (Optional[str]): Prefix attribute like => "/" for qresource.

        Returns:
            list: A list of all <file> subelement contained in qresource
                designated by the `prefix` or all qrc's <file> if no prefix.

        Raises:
            :class:`QresourceError`: Raised when the passed prefix doesn't
                correspond to any existing <qresource> node in the qrc file.

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
        """Generate qrc file in function with path and name attributes."""
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

    @property
    def tree(self):
        return self._tree

    @property
    def root(self):
        return self._root

    @property
    def qresources(self):
        return self._qresources


def read_qrc(qrc):
    """Parse a qrc file to return a QRCFile object.

    Args:
        qrc (str): Path to the qrc file.

    Returns:
        :class:`QRCFile`: :class:`QRCFile` representing passed qrc file.

    Raised:
        :class:`QRCFileError`: Raised when passed qrc file does not exist.

    """
    if not os.path.isfile(qrc):
        raise QRCFileError("Error: Qrc file \'{}\' does not exist.".format(qrc))

    path, name = os.path.split(qrc)
    qrcfile = QRCFile(name, path)

    parser = etree.XMLParser(remove_blank_text=True)
    qrcfile._tree = etree.parse(qrc, parser)
    qrcfile._root = qrcfile.tree.getroot()

    for qresource in qrcfile.root.iter(tag="qresource"):
        qrcfile.qresources.append(qresource)

    return qrcfile


def fill_qresource(qrc, folder, prefix):
    """Fill a qrc with resources contained in the passed folder.

    Each file of resource folder will be record as <file> subelement of the
    corresponding qresource element (see prefix). The value of the subelement
    is the relative path between the resource within the folder and the
    project directory.

    Args:
        qrc (:class:`QRCFile`): A QRCFile object to add and fill qresource.
        folder (str): Path to the folder of resources to record.
        prefix (str): <qresource>'s prefix in which add the <file>.

    """
    # In case where the prefix is root, only files in root of the folder
    # will be recorded as <file> subelement.
    if prefix == "/":
        for resource in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, resource)):
                # Relative path between qrc file and the project directory
                path = os.path.relpath(os.path.join(folder, resource),
                                       os.path.dirname(find_project_config()))
                qrc.add_file(path, prefix)
        return

    # Otherwise all files are recorded recursively
    for root, dirs, files in os.walk(folder):
        for resource in files:
            resource_path = os.path.join(root, resource)

            # Relative path between qrc file and the project directory
            path = os.path.relpath(
                    resource_path, os.path.dirname(find_project_config()))

            qrc.add_file(path, prefix)


def generate_qrc(qrc, res_folder, build=True):
    """Generate qrc file with provided folder of resources. The root of the
    resources folder correspond to qresource with "/" prefix. Resources that are
    not in folders will be recorded a <file> subelement to "/" qresource.
    For each directory present in the resources folder a qresource with
    "/" + directory's name as prefix will be created. In each of these
    directory, files are recursively recorded in corresponding qresource.

    Args:
        qrc (:class:`QRCFile`): A newly created QRCFile.
        res_folder (str): Path to the folder of resources.
        build (Optional[bool]): If True `QRCFile` object is save into qrc file.

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


def get_prefix(path):
    """Generate a prefix for qresource in function of the passed path.

    Args:
        path (str): Relative path of a folder of resources from project dir.

    Returns;
        str: Prefix corresponding to `path`

    """
    # Remove finishing separator from path if exist
    if path[-1] == os.sep:
        path = path[:-1]

    # Return the prefix corresponding to the path
    return "/" + os.path.basename(path)


def get_prefix_update(path):
    """
    Generate a prefix for qresource in function of the passed path for
    update command.

    Args:
        path (str): Relative path of a folder of resources from project dir.

    Returns;
        str: Prefix corresponding to `path`

    """
    # Remove finishing separator from path if exist
    if path[-1] == os.sep:
        path = path[:-1]

    # Return the prefix corresponding to the path
    if os.path.split(path)[0] == "":
        return "/"
    else:
        return "/" + os.path.basename(path)
