"""This module enable user to generate qrc file for qt project."""

import os
import sys

from lxml import etree
from functools import wraps


class GenerativeBase(object):
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


class QRCFile(GenerativeBase):
    """Class generating qrc file.

    Attributes:
        name (str): File name of the new qrc file.
        path (optional[str]): Path to new qrc file.
        _qresources (list[etree.SubElement]): List of qresources created.
        _last_qresource (etree.SubElement): Last qresource created.
        _root (etree.Element): Root element of qrc file.
        _tree (etree.ElementTree): Qrc tree with added qresources and resources.


    Example:
        >>>(
        ...    QRCFile("test")
        ...    .add_qresource("/")
        ...    .add_file("test.txt")
        ...    .add_file("test1.txt")
        ...    .add_qresource("/images")
        ...    .add_file("img.png")
        ...    .build()
        ...)

    """

    def __init__(self, name, path="."):
        self.name = name
        self.path = os.path.join(path, name + ".qrc")
        self._qresources = []
        self._last_qresource = None
        self._root = etree.Element("RCC")
        self._tree = etree.ElementTree(self._root)

    @chain
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

    @chain
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

    @chain
    def build(self):
        """Generate qrc file in function avec path and name attribute."""
        with open(self.path, "w") as f:
            f.write(etree.tostring(
                self._tree, pretty_print=True).decode('utf-8')
            )
