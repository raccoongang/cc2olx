import re
from typing import Dict, Optional

from cc2olx import filesystem
from cc2olx.constants import WEB_LINK_NAMESPACE
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import Cartridge


class WebLinkParserMixin:
    """
    Provide Common Cartridge Web Link resource parsing functionality.
    """

    _cartridge: Cartridge

    def _parse_web_link_content(self, resource: dict) -> Optional[Dict[str, str]]:
        """
        Provide Web Link resource data.
        """
        if web_link_match := re.match(CommonCartridgeResourceType.WEB_LINK, resource["type"]):
            res_file_path = self._cartridge.build_res_file_path(resource["children"][0].href)
            tree = filesystem.get_xml_tree(res_file_path)
            root = tree.getroot()
            ns = self._build_web_link_namespace(web_link_match)
            title = root.find("wl:title", ns).text
            url = root.find("wl:url", ns).get("href")
            return {"href": url, "text": title}
        return None

    @staticmethod
    def _build_web_link_namespace(web_link_match: re.Match) -> Dict[str, str]:
        """
        Build Web Link namespace.
        """
        web_link = WEB_LINK_NAMESPACE.format(
            major_version=web_link_match.group("major_version"),
            minor_version=web_link_match.group("minor_version"),
        )
        return {"wl": web_link}
