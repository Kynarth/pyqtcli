"""Functions for the update command of pyqtcli cli."""

import os

from pyqtcli import verbose as v
from pyqtcli.cli import read_qrc
from pyqtcli.qrc import get_prefix_update
from pyqtcli.config import find_project_config


def update_project(qrc_files, config, verbose):
    """Update given qrc files through information stored in the config file.

    Args:
        qrc_files (list or tuple): list of paths to qrc files.
        config (:class:`pyqtcli.config.PyqtcliConfig`): Project config file.
        verbose (bool): If True display information about the process

    """
    for qrc_file in qrc_files:
        qrc = read_qrc(qrc_file)          # qrc file to update
        dirs = config.get_dirs(qrc.name)  # resources folders recorded in qrc

        for res_dir in dirs:
            if os.path.abspath(res_dir) == os.path.dirname(
                    find_project_config()):
                v.warning("Can't update automatically a qrc file where "
                          "resources are in the same directory as the project "
                          "one.")
                continue

            # prefix identify qresource in qrc file
            prefix = get_prefix_update(res_dir)

            # Verify the recorded directory still exist and otherwise remove
            # it from dirs variable in config file. It's corresponding in qrc
            # file is deleted with its <file> children
            if not os.path.isdir(res_dir):
                config.rm_dirs(qrc.name, res_dir)
                qrc.remove_qresource(prefix)
                qrc.build()

                v.info(
                    ("The resource folder {} has been manually removed.\n"
                     "It's resources are removed from {} and deleted "
                     "from .pyqtclirc").format(res_dir, qrc_file), verbose
                )
                continue

            # Loop over the folder of resources to check file addition or
            # deletion to report in qrc file
            resources = qrc.list_resources(prefix)
            if prefix == "/":
                # list of resources at the root
                res = []
                for path in os.listdir(res_dir):
                    if os.path.isfile(os.path.join(res_dir, path)):
                        res.append(path)

                new_qresource_dirs = [r for r in res if r not in dirs]
                for resource in res:
                    # A new folder in the root of resources folder as been added
                    resource = os.path.join(res_dir, resource)
                    if os.path.isdir(os.path.join(res_dir, resource)) and \
                            resource in new_qresource_dirs:
                        qrc.add_qresource(
                            get_prefix_update(os.path.join(res_dir, resource)),
                            res_dir
                        )
                        v.info("{} added to {} as {}".format(
                                res_dir, qrc_file, prefix), verbose)
                    else:
                        # Add the resource if not recorded
                        if resource not in resources:
                            qrc.add_file(resource, prefix)
                            v.info("{} added to {}".format(resource, qrc_file),
                                   verbose)
                        # Remove the resource if it's recorded
                        elif resource in resources:
                            resources.remove(resource)
            else:
                for root, dirs, files in os.walk(res_dir):
                    for resource in files:
                        resource = os.path.join(root, resource)
                        # Add the resource if not recorded
                        if resource not in resources:
                            qrc.add_file(resource, prefix)
                            v.info("{} added to {}".format(resource, qrc_file),
                                   verbose)
                        # Remove the resource if it's recorded
                        elif resource in resources:
                            resources.remove(resource)

            # Remaining resources in resources variable have been deleted
            # manually and so removed from qrc
            for res in resources:
                qrc.remove_resource(res, prefix)
                v.info(
                    ("The resource \'{}\' has been manually deleted and so"
                     " removed from {}").format(res, qrc_file), verbose)

        # Save modifications to qrc file
        qrc.build()
