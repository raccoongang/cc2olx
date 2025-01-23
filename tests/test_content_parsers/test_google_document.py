from unittest.mock import Mock

import pytest

from cc2olx.content_parsers import GoogleDocumentContentParser


class TestGoogleDocumentContentParser:
    parser_type = GoogleDocumentContentParser

    def test_parse_webcontent_transforms_web_link_content_to_google_document(self):
        parser = self.parser_type(Mock(), Mock())
        web_link_content_mock = Mock()
        transform_web_link_content_to_google_document = Mock()
        parser._parse_web_link_content = Mock(return_value=web_link_content_mock)
        parser._transform_web_link_content_to_google_document = transform_web_link_content_to_google_document
        resource = {"type": "imswl_xmlv1p3"}

        parsed_content = parser._parse_resource_content(resource)

        parser._parse_web_link_content.assert_called_once_with(resource)
        transform_web_link_content_to_google_document.assert_called_once_with(web_link_content_mock)
        assert parsed_content == transform_web_link_content_to_google_document.return_value

    @pytest.mark.parametrize(
        "web_link_url",
        [
            "https://docs.google.com/drawings/d/e/2PACX-1vTDskPsAcSoDz6D0swCEuf9n7R67X0zuaDLIrDorbon9/pub?w=960&h=720",
            "https://docs.google.com/document/u/0/?tgif=d",
            "https://docs.google.com/spreadsheets/u/1/",
            "/2PACX-1vTDskPsAcSoDz6D0swCEuf9n7R67X0zuaDLIrDorbon9/pub?w=960&h=720",
            "https://example.com",
            "http://example.com",
        ],
    )
    def test_transform_web_link_content_to_google_document_when_web_link_points_to_unsupported_url(self, web_link_url):
        parser = self.parser_type(Mock(), Mock())
        web_link_content = {"href": web_link_url}

        assert parser._transform_web_link_content_to_google_document(web_link_content) is None

    @pytest.mark.parametrize(
        "web_link_url",
        [
            "https://docs.google.com/document/d/e/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/edit",
            "https://docs.google.com/document/d/e/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "https://docs.google.com/document/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "http://docs.google.com/document/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "https://docs.google.com/spreadsheets/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "https://docs.google.com/spreadsheets/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM",
            "http://docs.google.com/presentation/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDM/embed?start=true&loop=true",
            "https://docs.google.com/forms/d/e/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/alreadyresponded",
        ],
    )
    def test_transform_web_link_content_to_google_document_when_web_link_points_to_supported_url(self, web_link_url):
        parser = self.parser_type(Mock(), Mock())
        web_link_content = {"href": web_link_url}
        expected_content = {"url": web_link_url}

        actual_content = parser._transform_web_link_content_to_google_document(web_link_content)

        assert actual_content == expected_content
