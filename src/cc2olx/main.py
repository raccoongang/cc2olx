import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

import django

from cc2olx import filesystem
from cc2olx import olx
from cc2olx.cli import parse_args, RESULT_TYPE_FOLDER, RESULT_TYPE_ZIP
from cc2olx.constants import OLX_STATIC_DIR
from cc2olx.models import Cartridge
from cc2olx.settings import collect_settings


def convert_one_file(
    input_file,
    workspace,
    link_file=None,
    passport_file=None,
    relative_links_source=None,
):
    filesystem.create_directory(workspace)

    cartridge = Cartridge(input_file, workspace)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    olx_export = olx.OlxExport(cartridge, link_file, passport_file, relative_links_source)
    olx_filename = cartridge.directory.parent / (cartridge.directory.name + "-course.xml")
    policy_filename = cartridge.directory.parent / "policy.json"

    with open(str(olx_filename), "w", encoding="utf-8") as olxfile:
        olxfile.write(olx_export.xml())

    with open(str(policy_filename), "w", encoding="utf-8") as policy:
        policy.write(olx_export.policy())

    tgz_filename = (workspace / cartridge.directory.name).with_suffix(".tar.gz")

    file_list = [
        (str(olx_filename), "course.xml"),
        (str(policy_filename), "policies/course/policy.json"),
        (str(cartridge.directory / "web_resources"), "/{}/".format(OLX_STATIC_DIR)),
    ]

    # Add static files that are outside of web_resources directory
    file_list += [
        (str(cartridge.directory / original_filepath), olx_static_path)
        for olx_static_path, original_filepath in cartridge.olx_to_original_static_file_paths.extra.items()
    ]

    filesystem.add_in_tar_gz(str(tgz_filename), file_list)


def main():
    initialize_django()

    parsed_args = parse_args()
    settings = collect_settings(parsed_args)

    workspace = settings["workspace"]
    link_file = settings["link_file"]
    passport_file = settings["passport_file"]
    relative_links_source = settings["relative_links_source"]

    # setup logger
    logging_config = settings["logging_config"]
    logging.basicConfig(level=logging_config["level"], format=logging_config["format"])
    logger = logging.getLogger()

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_workspace = Path(tmpdirname) / workspace.stem

        for input_file in settings["input_files"]:
            try:
                convert_one_file(
                    input_file,
                    temp_workspace,
                    link_file,
                    passport_file,
                    relative_links_source,
                )

            except Exception:
                logger.exception("Error while converting %s file", input_file)

        if settings["output_format"] == RESULT_TYPE_FOLDER:
            shutil.rmtree(str(workspace), ignore_errors=True)
            shutil.copytree(str(temp_workspace), str(workspace))

        if settings["output_format"] == RESULT_TYPE_ZIP:
            shutil.make_archive(str(workspace), "zip", str(temp_workspace))

    logger.info("Conversion completed")

    return 0


def initialize_django():
    """
    Initialize the Django package.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc2olx.django_settings")
    django.setup()


if __name__ == "__main__":
    sys.exit(main())
