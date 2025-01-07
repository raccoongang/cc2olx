import re
from typing import Dict, Optional

from lxml import etree

from cc2olx import filesystem
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.utils import simple_slug


class LtiContentParser(AbstractContentParser):
    """
    LTI resource content parser.
    """

    NAMESPACES = {
        "blti": "http://www.imsglobal.org/xsd/imsbasiclti_v1p0",
        "lticp": "http://www.imsglobal.org/xsd/imslticp_v1p0",
        "lticm": "http://www.imsglobal.org/xsd/imslticm_v1p0",
    }
    DEFAULT_WIDTH = "500"
    DEFAULT_HEIGHT = "500"

    def _parse_content(self, idref: Optional[str]) -> Optional[dict]:
        if (
            idref
            and (resource := self._cartridge.define_resource(idref))
            and re.match(CommonCartridgeResourceType.LTI_LINK, resource["type"])
        ):
            data = self._parse_lti(resource)
            # Canvas flavored courses have correct url in module meta for lti links
            if self._cartridge.is_canvas_flavor:
                if item_data := self._cartridge.module_meta.get_external_tool_item_data(idref):
                    data["launch_url"] = item_data.get("url", data["launch_url"])
            return data
        return None

    def _parse_lti(self, resource: dict) -> dict:
        """
        Parse LTI resource.
        """
        res_file_path = self._cartridge.build_res_file_path(resource["children"][0].href)
        tree = filesystem.get_xml_tree(res_file_path)
        root = tree.getroot()
        title = root.find("blti:title", self.NAMESPACES).text
        description = root.find("blti:description", self.NAMESPACES).text
        data = {
            "title": title,
            "description": description,
            "launch_url": self._parse_launch_url(root),
            "height": self._parse_height(root),
            "width": self._parse_width(root),
            "custom_parameters": self._parse_custom_parameters(root),
            "lti_id": self._parse_lti_id(root, title),
        }
        return data

    def _parse_launch_url(self, resource_root: etree._Element) -> str:
        """
        Parse URL to launch LTI.
        """
        if (launch_url := resource_root.find("blti:secure_launch_url", self.NAMESPACES)) is None:
            launch_url = resource_root.find("blti:launch_url", self.NAMESPACES)
        return "" if launch_url is None else launch_url.text

    def _parse_width(self, resource_root: etree._Element) -> str:
        """
        Parse width.
        """
        width = resource_root.find("blti:extensions/lticm:property[@name='selection_width']", self.NAMESPACES)
        return self.DEFAULT_WIDTH if width is None else width.text

    def _parse_height(self, resource_root: etree._Element) -> str:
        """
        Parse height.
        """
        height = resource_root.find("blti:extensions/lticm:property[@name='selection_height']", self.NAMESPACES)
        return self.DEFAULT_HEIGHT if height is None else height.text

    def _parse_custom_parameters(self, resource_root: etree._Element) -> Dict[str, str]:
        """
        Parse custom parameters.
        """
        custom = resource_root.find("blti:custom", self.NAMESPACES)
        return {} if custom is None else {option.get("name"): option.text for option in custom}

    def _parse_lti_id(self, resource_root: etree._Element, title: str) -> str:
        """
        Parse LTI identifier.
        """
        # For Canvas flavored CC, tool_id can be used as lti_id if present
        tool_id = resource_root.find("blti:extensions/lticm:property[@name='tool_id']", self.NAMESPACES)
        # fmt: off
        return (
            simple_slug(title) if tool_id is None  # Create a simple slug lti_id from title
            else tool_id.text
        )
        # fmt: on
