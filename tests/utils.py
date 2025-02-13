import itertools
from typing import List

import xmlformatter

formatter = xmlformatter.Formatter(compress=True, encoding_output="UTF-8")


def format_xml(xml):
    return formatter.format_string(xml)


def build_multi_value_args(arg_name: str, values: List[str]) -> List[str]:
    """
    Build arguments list for multi-value arguments.
    """
    return list(itertools.chain(*[(arg_name, value) for value in values]))
