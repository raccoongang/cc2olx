import re
from typing import Dict, Optional

from cc2olx import filesystem
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import ResourceFile


class DiscussionContentParser(AbstractContentParser):
    """
    Discussion resource content parser.
    """

    NAMESPACES = {
        "imsdt_xmlv1p1": "http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1",
        "imsdt_xmlv1p2": "http://www.imsglobal.org/xsd/imsccv1p2/imsdt_v1p2",
        "imsdt_xmlv1p3": "http://www.imsglobal.org/xsd/imsccv1p3/imsdt_v1p3",
    }

    def _parse_content(self, idref: Optional[str]) -> Optional[Dict[str, str]]:
        if (
            idref
            and (resource := self._cartridge.define_resource(idref))
            and re.match(CommonCartridgeResourceType.DISCUSSION_TOPIC, resource["type"])
        ):
            data = self._parse_discussion(resource)
            return data

    def _parse_discussion(self, resource: dict) -> Dict[str, str]:
        """
        Parse the discussion content.
        """
        data = {}

        for child in resource["children"]:
            if isinstance(child, ResourceFile):
                data.update(self._parse_resource_file_data(child, resource["type"]))

        return data

    def _parse_resource_file_data(self, resource_file: ResourceFile, resource_type: str) -> Dict[str, str]:
        """
        Parse the discussion resource file.
        """
        tree = filesystem.get_xml_tree(self._cartridge.build_res_file_path(resource_file.href))
        root = tree.getroot()
        ns = {"dt": self.NAMESPACES[resource_type]}
        title = root.find("dt:title", ns).text
        text = root.find("dt:text", ns).text
        return {"title": title, "text": text}
