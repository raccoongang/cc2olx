import urllib
from typing import Dict, Optional

from cc2olx.content_parsers import AbstractContentTypeWithCustomBlockParser
from cc2olx.content_parsers.mixins import WebLinkParserMixin
from cc2olx.content_parsers.utils import WebContent
from cc2olx.enums import CommonCartridgeResourceType, SupportedCustomBlockContentType


class PdfContentParser(WebLinkParserMixin, AbstractContentTypeWithCustomBlockParser):
    """
    PDF resource content parser.
    """

    CUSTOM_BLOCK_CONTENT_TYPE = SupportedCustomBlockContentType.PDF

    def _parse_resource_content(self, resource: dict) -> Optional[Dict[str, str]]:
        if resource["type"] == CommonCartridgeResourceType.WEB_CONTENT:
            return self._parse_webcontent(resource)
        elif web_link_content := self._parse_web_link_content(resource):
            return self._transform_web_link_content_to_pdf(web_link_content)
        return None

    def _parse_webcontent(self, resource: dict) -> Optional[Dict[str, str]]:
        """
        Parse the resource with "webcontent" type.
        """
        web_content = WebContent(self._cartridge, resource["children"][0])
        resource_file_path = web_content.resource_file_path

        if resource_file_path.suffix in SupportedCustomBlockContentType.PDF.file_extensions:
            return (
                self._parse_pdf_webcontent_from_web_resources_dir(web_content)
                if web_content.is_from_web_resources_dir()
                else self._parse_pdf_webcontent_outside_web_resources_dir(web_content)
            )
        return None

    def _parse_pdf_webcontent_from_web_resources_dir(self, web_content: WebContent) -> Dict[str, str]:
        """
        Parse webcontent PDF file from "web_resources" directory.
        """
        olx_static_path = web_content.olx_static_path
        self._cartridge.olx_to_original_static_file_paths.add_web_resource_path(
            olx_static_path,
            web_content.resource_file_path,
        )
        return {"url": olx_static_path}

    def _parse_pdf_webcontent_outside_web_resources_dir(self, web_content: WebContent) -> Dict[str, str]:
        """
        Parse webcontent PDF file located outside "web_resources" directory.
        """
        olx_static_path = web_content.olx_static_path
        self._cartridge.olx_to_original_static_file_paths.add_extra_path(
            olx_static_path,
            web_content.resource_relative_path,
        )
        return {"url": olx_static_path}

    @staticmethod
    def _transform_web_link_content_to_pdf(web_link_content: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Build PDF block data from Web Link resource data.
        """
        web_link_url = web_link_content["href"]
        does_web_link_point_to_pdf_file = any(
            urllib.parse.urlparse(web_link_url).path.endswith(file_extension)
            for file_extension in SupportedCustomBlockContentType.PDF.file_extensions
        )
        return {"url": web_link_url} if does_web_link_point_to_pdf_file else None
