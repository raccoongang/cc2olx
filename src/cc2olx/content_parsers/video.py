import re
from typing import Dict, Optional

from cc2olx.constants import YOUTUBE_LINK_PATTERN
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.content_parsers.mixins import WebLinkParserMixin


class VideoContentParser(WebLinkParserMixin, AbstractContentParser):
    """
    Video resource content parser.
    """

    def _parse_content(self, idref: Optional[str]) -> Optional[Dict[str, str]]:
        if (
            idref
            and (resource := self._cartridge.define_resource(idref))
            and (web_link_content := self._parse_web_link_content(resource))
            and (youtube_match := re.search(YOUTUBE_LINK_PATTERN, web_link_content["href"]))
        ):
            return {"youtube": youtube_match.group("video_id")}
        return None
