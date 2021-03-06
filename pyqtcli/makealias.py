import os

from lxml import etree

from pyqtcli import verbose as v

WARNING_TEMPLATE = "Alias \'{}\' already exists in \'{}\' at prefix \'{}\'."


def write_alias(qrc_files, verbose):
    """Write alias for resources within qrc files.

    Alias are base in basename of theses resources. In the case where two
    resource files would have the same name, and so, the same alias, the
    script warns the user of incriminated files.

    Args:
        qrc_files (list or tuple): A list containing path to qrc files.
        verbose (bool): True if the user pass '-v' or '--verbose' option
            to see what's happening.
    """
    warnings = []  # List containing all warnings message
    # Loop over all provided qrc files
    for qrc_file in qrc_files:
        tree = etree.parse(qrc_file)
        root = tree.getroot()

        # Inform which qrc file is processed
        v.info("Current file: {}".format(qrc_file), verbose)

        # Iterate over each qresource containing file resources
        for qresource in root.iter(tag="qresource"):
            # Alias are prefixed by qresource prefix so we check only
            # duplication within qresource
            aliases = []
            # Iterate over each file that doesn't have already an alias
            for resource in qresource.iter(tag="file"):
                alias = os.path.basename(resource.text)
                if alias not in aliases:
                    if not resource.attrib.get("alias", None):
                        resource.set("alias", alias)

                        # Inform which alias is given to the current resource
                        v.info("resource: '{}' => {}".format(
                            resource.text, alias), verbose)
                else:
                    # Add same alias warning
                    warnings.append(WARNING_TEMPLATE.format(
                        alias, qrc_file, qresource.attrib.get(
                            "prefix", ""))
                    )
                    break

                # Append created alias to used aliases in current qresource
                aliases.append(alias)

        # Rewrite qrc file
        tree.write(qrc_file)

    # Warning user of which resources that could not receive alias
    # because of duplication
    for message in warnings:
        v.warning(message)
