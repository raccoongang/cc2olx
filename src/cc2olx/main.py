import logging
import shutil
import sys
import tempfile
from pathlib import Path

from cc2olx import filesystem, olx, settings
from cc2olx.cli import parse_args, RESULT_TYPE_FOLDER, RESULT_TYPE_ZIP
from cc2olx.constants import OLX_STATIC_DIR
from cc2olx.models import Cartridge
from cc2olx.parser import parse_options


def convert_one_file(input_file, workspace, link_file=None, passport_file=None):
    filesystem.create_directory(workspace)

    cartridge = Cartridge(input_file, workspace)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    olx_export = olx.OlxExport(cartridge, link_file, passport_file)
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
        (str(cartridge.directory / filepath), "/static/{}".format(filepath))
        for filepath in cartridge.extra_static_files
    ]

    filesystem.add_in_tar_gz(str(tgz_filename), file_list)


def main():
    args = parse_args()
    options = parse_options(args)

    workspace = options["workspace"]
    link_file = options["link_file"]
    passport_file = options["passport_file"]

    # setup logger
    logging.basicConfig(level=options["log_level"], format=settings.LOG_FORMAT)
    logger = logging.getLogger()

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_workspace = Path(tmpdirname) / workspace.stem

        for input_file in options["input_files"]:
            try:
                convert_one_file(input_file, temp_workspace, link_file, passport_file)
            except Exception:
                logger.exception("Error while converting %s file", input_file)

        if options["output_format"] == RESULT_TYPE_FOLDER:
            shutil.rmtree(str(workspace), ignore_errors=True)
            shutil.copytree(str(temp_workspace), str(workspace))

        if options["output_format"] == RESULT_TYPE_ZIP:
            shutil.make_archive(str(workspace), "zip", str(temp_workspace))

    logger.info("Conversion completed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
