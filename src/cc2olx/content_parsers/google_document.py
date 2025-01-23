import re
from typing import Dict, Optional

from cc2olx.content_parsers import AbstractContentTypeWithCustomBlockParser
from cc2olx.content_parsers.mixins import WebLinkParserMixin
from cc2olx.enums import SupportedCustomBlockContentType


class GoogleDocumentContentParser(WebLinkParserMixin, AbstractContentTypeWithCustomBlockParser):
    """
    Google document resource content parser.
    """

    CUSTOM_BLOCK_CONTENT_TYPE = SupportedCustomBlockContentType.GOOGLE_DOCUMENT
    SUPPORTED_GOOGLE_DOCUMENT_URL_PATTERN = r"^https?:\/\/docs\.google\.com\/(?!drawings\/)([^\/]+)\/d\/.*$"

    def _parse_resource_content(self, resource: dict) -> Optional[Dict[str, str]]:
        if web_link_content := self._parse_web_link_content(resource):
            return self._transform_web_link_content_to_google_document(web_link_content)
        return None

    def _transform_web_link_content_to_google_document(
        self,
        web_link_content: Dict[str, str],
    ) -> Optional[Dict[str, str]]:
        """
        Build Google document block data from Web Link resource data.
        """
        web_link_url = web_link_content["href"]
        return (
            {"url": web_link_url} if re.match(self.SUPPORTED_GOOGLE_DOCUMENT_URL_PATTERN, web_link_url, re.I) else None
        )
