from unittest.mock import Mock, patch

from cc2olx.content_parsers import AbstractContentTypeWithCustomBlockParser


@patch("cc2olx.content_parsers.abc.AbstractContentTypeWithCustomBlockParser.__abstractmethods__", frozenset())
class TestAbstractContentTypeWithCustomBlockParser:
    parser_type = AbstractContentTypeWithCustomBlockParser

    def test_parse_content_returns_none_if_idref_is_none(self):
        parser = self.parser_type(Mock(), Mock())

        assert parser._parse_content(None) is None

    def test_parse_content_returns_none_if_content_type_with_custom_block_is_not_used(self):
        parser = self.parser_type(Mock(), Mock())
        parser._context = Mock(is_content_type_with_custom_block_used=Mock(return_value=False))
        parser.CUSTOM_BLOCK_CONTENT_TYPE = Mock()

        assert parser._parse_content(Mock()) is None

    def test_parse_content_returns_none_if_resource_is_not_found(self):
        parser = self.parser_type(Mock(), Mock())
        parser._context = Mock(is_content_type_with_custom_block_used=Mock(return_value=True))
        parser._cartridge = Mock(define_resource=Mock(return_value=None))
        parser.CUSTOM_BLOCK_CONTENT_TYPE = Mock()

        assert parser._parse_content(Mock()) is None
