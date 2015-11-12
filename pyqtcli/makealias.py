import os
import click

import xml.etree.ElementTree as ET


def write_alias(qrc_files, verbose):
    """Write alias for resources within qrc files.

    Alias are base in basename of theses resources.

    Args:
        qrc_files (tuple): A tuple containing path to qrc files.
        verbose (bool): True if the user pass '-v' or '--verbose' option
            to see what's happening.
    """
    for qrc_file in qrc_files:
        tree = ET.parse(qrc_file)
        root = tree.getroot()
        aliases = []

        for resource in root.iter(tag="file"):
            alias = os.path.basename(resource.text)
            if alias not in aliases:
                if not resource.attrib.get("alias", None):
                    resource.set("alias", alias)
            else:
                click.secho(
                    "Error: alias '{}' already exists.".format(alias),
                    err=True, fg="red")
                break

            aliases.append(alias)

        tree.write(qrc_file)
