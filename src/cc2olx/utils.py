""" Utility functions for cc2olx"""

import logging
import string
import csv
import re
import sys
from importlib import import_module
from typing import Type

from cc2olx.constants import CDATA_PATTERN

logger = logging.getLogger()


def element_builder(xml_doc):
    """
    Given a document returns a function to build xml elements.

    Args:
        xml_doc (xml.dom.minidom.Document)

    Returns:
        element (func)
    """

    def element(name, children, attributes=None):
        """
        An utility to help build xml tree in a managable way.

        Args:
            name (str) - tag name
            children (str|list|xml.dom.minidom.Element)
            attributes (dict)

        Returns:
            elem (xml.dom.minidom.Element)
        """

        elem = xml_doc.createElement(name)

        # set attributes if exists
        if attributes is not None and isinstance(attributes, dict):
            [elem.setAttribute(key, val) for key, val in attributes.items()]

        # set children if exists
        if children is not None:
            if isinstance(children, list) or isinstance(children, tuple):
                [elem.appendChild(c) for c in children]
            elif isinstance(children, str):
                elem.appendChild(xml_doc.createTextNode(children))
            else:
                elem.appendChild(children)

        return elem

    return element


def simple_slug(value: str):
    char_to_convert = string.punctuation + " "
    slug = "".join(char if char not in char_to_convert else "_" for char in value)
    return slug.replace("__", "_").strip("_").lower()


def passport_file_parser(filename: str):
    """
    Reads and parse passport file.

    Args:
        filename (str) - path of the file containing lti consumer details

    Returns:
        passports (dict) - Dictionary with lti consumer id and corresponding passports
    """
    required_fields = ["consumer_id", "consumer_key", "consumer_secret"]
    with open(filename, "r", encoding="utf-8") as csvfile:
        passport_file = csv.DictReader(csvfile)

        # Validation: File should contain the required headers.
        headers = passport_file.fieldnames or []
        fields_in_header = [field in headers for field in required_fields]
        if not all(fields_in_header):
            logger.warning(
                "Ignoring passport file (%s). Please ensure that the file"
                " contains required headers consumer_id, consumer_key and consumer_secret.",
                filename,
            )
            return {}

        passports = dict()
        for row in passport_file:
            passport = "{lti_id}:{key}:{secret}".format(
                lti_id=row["consumer_id"], key=row["consumer_key"], secret=row["consumer_secret"]
            )
            passports[row["consumer_id"]] = passport

        return passports


def clean_file_name(filename: str):
    """
    Replaces any reserved characters with an underscore so the filename can be used in read and write
    operations

    Args:
        filename (str) - path of the file to be cleaned

    Returns:
        filename (str) - filename with the reserved characters removed
    """
    special_characters = r"[\?\*\|:><]"

    cleaned_name = re.sub(special_characters, "_", filename)
    return cleaned_name


def clean_from_cdata(xml_string: str) -> str:
    """
    Deletes CDATA tag from XML string while keeping its content.

    Args:
        xml_string (str): original XML string to clean.

    Returns:
        str: cleaned XML string.
    """
    return re.sub(CDATA_PATTERN, r"\g<content>", xml_string, flags=re.DOTALL)


def cached_import(module_path: str, class_name: str) -> Type:
    """
    Provide the module from the cache or import it if it is not already loaded.
    """
    # Check whether module is loaded and fully initialized.
    if not (
        (module := sys.modules.get(module_path))
        and (spec := getattr(module, "__spec__", None))
        and getattr(spec, "_initializing", False) is False
    ):
        module = import_module(module_path)
    return getattr(module, class_name)


def import_string(dotted_path: str) -> Type:
    """
    Import a dotted module path.

    Provide the attribute/class designated by the last name in the path.
    Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    try:
        return cached_import(module_path, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (module_path, class_name)) from err
