from collections import ChainMap
from types import MappingProxyType
from typing import Callable, Dict, List, NamedTuple, Optional, Set

import attrs

from cc2olx.iframe_link_parser import IframeLinkParser


@attrs.define(slots=False)
class OlxToOriginalStaticFilePaths:
    """
    Provide OLX static file to Common cartridge static file mappings.
    """

    # Static files from `web_resources` directory
    _web_resources: Dict[str, str] = attrs.field(factory=dict)
    # Static files that are outside of `web_resources` directory, but still required
    _extra: Dict[str, str] = attrs.field(factory=dict)

    @property
    def extra(self) -> MappingProxyType:
        """
        Provide static files located outside "web_resources" directory.

        The returned value is read-only mapping.
        """
        return MappingProxyType(self._extra)

    def add_web_resource_path(self, olx_static_path: str, cc_static_path: str) -> None:
        """
        Add web resource static file mapping.
        """
        self._web_resources[olx_static_path] = cc_static_path

    def add_extra_path(self, olx_static_path: str, cc_static_path: str) -> None:
        """
        Add extra static file mapping.
        """
        self._extra[olx_static_path] = cc_static_path

    def __attrs_post_init__(self) -> None:
        self.all = ChainMap(self._extra, self._web_resources)


class LinkKeywordProcessor(NamedTuple):
    """
    Encapsulate a link keyword and it's processor.
    """

    keyword: str
    processor: Callable[[str, str], str]


class FibProblemRawAnswers(NamedTuple):
    """
    Encapsulate answers data for a Fill-In-The-Blank problem.
    """

    exact_answers: List[str]
    answer_patterns: List[str]


@attrs.define(frozen=True, slots=False)
class OlxGeneratorContextMixin:
    """
    Encapsulate an OLX generator context data.
    """

    iframe_link_parser: Optional[IframeLinkParser]
    _lti_consumer_ids: Set[str]

    def add_lti_consumer_id(self, lti_consumer_id: str) -> None:
        """
        Populate LTI consumer IDs set with a provided value.
        """
        self._lti_consumer_ids.add(lti_consumer_id)


class OlxGeneratorContext(OlxGeneratorContextMixin):
    """
    Encapsulate an OLX generator context.

    Provide additional initialization methods.
    """

    @classmethod
    def from_content_processor_context(
        cls,
        content_processor_context: "ContentProcessorContext",
    ) -> "OlxGeneratorContext":
        """
        Create the OLX generator context from the content processor context.
        """
        return cls(
            iframe_link_parser=content_processor_context.iframe_link_parser,
            lti_consumer_ids=content_processor_context._lti_consumer_ids,
        )


@attrs.define(frozen=True, slots=False)
class ContentParserContextMixin:
    """
    Encapsulate a content parser context data.
    """

    relative_links_source: Optional[str]
    _content_types_with_custom_blocks: List[str]

    def is_content_type_with_custom_block_used(self, content_type: str) -> bool:
        """
        Decide whether a content type with custom block is used.
        """
        return content_type in self._content_types_with_custom_blocks


class ContentParserContext(ContentParserContextMixin):
    """
    Encapsulate a content parser context.

    Provide additional initialization methods.
    """

    @classmethod
    def from_content_processor_context(
        cls,
        content_processor_context: "ContentProcessorContext",
    ) -> "ContentParserContext":
        """
        Create the content parser context from the content processor context.
        """
        return cls(
            content_processor_context.relative_links_source,
            content_processor_context._content_types_with_custom_blocks,
        )


@attrs.define(frozen=True, slots=False)
class ContentProcessorContext(ContentParserContextMixin, OlxGeneratorContextMixin):
    """
    Encapsulate a content processor context.
    """
