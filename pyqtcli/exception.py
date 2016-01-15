"""This module regroups all exceptions tied to pyqtcli cli."""


class QresourceError(Exception):
    """Exception raised with problems concerning qresource node in qrc files."""
    def __init__(self, arg):
        super(QresourceError, self).__init__()
        self.msg = arg

    def __str__(self):
        return self.msg


class PyqtcliConfigError(Exception):
    """Exception raised with problems concerning .pyqtclirc config file."""
    def __init__(self, arg):
        super(PyqtcliConfigError, self).__init__()
        self.msg = arg

    def __str__(self):
        return self.msg


class QRCFileError(Exception):
    """Exception raised with problems concerning qrc files."""
    def __init__(self, arg):
        super(QRCFileError, self).__init__()
        self.msg = arg

    def __str__(self):
        return self.msg
