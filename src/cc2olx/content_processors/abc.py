import xml.dom.minidom
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, TypeVar, Union

from cc2olx.content_processors.content_modifiers import StaticLinkModifier
from cc2olx.content_processors.dataclasses import ContentProcessorContext
from cc2olx.models import Cartridge

Content = TypeVar("Content", List[dict], dict)


class AbstractContentProcessor(ABC):
    """
    Abstract base class for Common Cartridge content processing.
    """

    def __init__(self, cartridge: Cartridge, context: ContentProcessorContext) -> None:
        self._cartridge = cartridge
        self._context = context
        self._doc = xml.dom.minidom.Document()

    def process(self, idref: Optional[str]) -> Optional[List[xml.dom.minidom.Element]]:
        """
        Process a Common Cartridge resource content.
        """
        if content := self._parse(idref):
            content = self._modify_content(content)
            olx_nodes = self._create_nodes(content)
            self._post_process(content)
            return olx_nodes
        return None

    @abstractmethod
    def _parse(self, idref: Optional[str]) -> Optional[Union[list, dict]]:
        """
        Parse content of the resource with the specified identifier.
        """

    @abstractmethod
    def _create_nodes(self, content: Union[dict, List[dict]]) -> List[xml.dom.minidom.Element]:
        """
        Create OLX nodes.
        """

    def _modify_content(self, content: Content) -> Content:
        """
        Perform content modification.
        """
        for content_modifier in self._get_content_modifiers():
            content = content_modifier(content)
        return content

    def _get_content_modifiers(self) -> List[Callable[[Content], Content]]:
        """
        Provide content modifiers.
        """
        return [self._modify_static_links]

    def _modify_static_links(self, content: Content) -> Content:
        """
        Apply static link modifications to content.
        """
        link_processor = StaticLinkModifier(self._cartridge, self._context.relative_links_source)
        return link_processor.process_content_static_links(content)

    def _post_process(self, content: Union[dict, List[dict]]) -> None:
        """
        Perform post-processing actions on content.
        """
