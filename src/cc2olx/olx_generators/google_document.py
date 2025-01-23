import html
import xml.dom.minidom
from typing import Dict, List

from lxml import etree

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import element_builder


class GoogleDocumentOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for Google documents.
    """

    # Standard iframe settings added by Google document xBlock by default.
    DEFAULT_GOOGLE_DOCUMENT_IFRAME_ATTRIBUTES = {
        "frameborder": "0",
        "width": "960",
        "height": "569",
        "allowfullscreen": "true",
        "mozallowfullscreen": "true",
        "webkitallowfullscreen": "true",
    }

    def create_nodes(self, content: Dict[str, str]) -> List[xml.dom.minidom.Element]:
        el = element_builder(self._doc)
        google_document_node = el("google-document", [], self._generate_google_document_attributes(content))
        return [google_document_node]

    def _generate_google_document_attributes(self, content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate Google document tag attributes.
        """
        google_document_iframe = self._create_google_document_iframe(content)
        google_document_iframe_string = html.unescape(
            etree.tostring(google_document_iframe, pretty_print=True, method="html").decode("utf-8")
        )
        return {"embed_code": google_document_iframe_string}

    def _create_google_document_iframe(self, content: Dict[str, str]) -> etree.ElementBase:
        """
        Create HTML iframe tag pointing to Google document.
        """
        return etree.Element("iframe", self._generate_google_document_iframe_attributes(content))

    def _generate_google_document_iframe_attributes(self, content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate Google document HTML iframe tag attributes.
        """
        return {
            **self.DEFAULT_GOOGLE_DOCUMENT_IFRAME_ATTRIBUTES,
            "src": content["url"],
        }
