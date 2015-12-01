import os
import sys

from functools import wraps

from pyqtcli.qrc import QRCFile


class GenerativeBase():
    def _generate(self):
        s = self.__class__.__new__(self.__class__)
        s.__dict__ = self.__dict__.copy()
        return s


def chain(func):
    @wraps(func)
    def decorator(self, *args, **kw):
        self = self._generate()
        func(self, *args, **kw)
        return self
    return decorator


class QRCTestFile(QRCFile, GenerativeBase):
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
        super(QRCTestFile, self).__init__(name, path)

    @chain
    def add_qresource(self, prefix=None):
        """Create to the qresource subelement.

        Args:
            prefix (str[optional]): Prefix attribute like => "/"
                for qresource element.

        """
        super().add_qresource(prefix)

    @chain
    def add_file(self, resource, prefix=None):
        """
        Add a file to the last added qresource and create its file in a
        dir corresponding to the qresource's prefix attribute.

        Args:
            resource (str): Path to the resource.

        """
        super().add_file(resource, prefix)

        # Create directories of the resource if not exists
        dir_name = os.path.join(
            os.path.split(self.path)[0],
            os.path.split(resource)[0]
        )

        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        resource = os.path.join(os.path.split(self.path)[0], resource)
        if not os.path.isfile(resource):
            open(resource, 'a').close()
        else:
            sys.exit("Error: the file: {} already exists.".format(resource))

    @chain
    def build(self):
        """Generate qrc file in function avec path and name attribute."""
        super().build()
