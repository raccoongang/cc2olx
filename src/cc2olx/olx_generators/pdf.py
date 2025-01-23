import xml.dom.minidom
from typing import List

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import element_builder


class PdfOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for PDFs.
    """

    def create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        el = element_builder(self._doc)
        pdf_node = el("pdf", [], {"url": content["url"]})
        return [pdf_node]
