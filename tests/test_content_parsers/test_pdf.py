from unittest.mock import Mock, patch

import pytest

from cc2olx.content_parsers import PdfContentParser


class TestPdfContentParser:
    parser_type = PdfContentParser

    def test_parse_resource_content_parses_webcontent(self):
        parser = self.parser_type(Mock(), Mock())
        resource = {"type": "webcontent"}
        parse_webcontent_mock = Mock()
        parser._parse_webcontent = parse_webcontent_mock

        parsed_content = parser._parse_resource_content(resource)

        parse_webcontent_mock.assert_called_once_with(resource)
        assert parsed_content == parse_webcontent_mock.return_value

    def test_parse_resource_content_transforms_web_link_content_to_pdf(self):
        parser = self.parser_type(Mock(), Mock())
        web_link_content_mock = Mock()
        transform_web_link_content_to_pdf_mock = Mock()
        parser._parse_web_link_content = Mock(return_value=web_link_content_mock)
        parser._transform_web_link_content_to_pdf = transform_web_link_content_to_pdf_mock
        resource = {"type": "imswl_xmlv1p3"}

        parsed_content = parser._parse_resource_content(resource)

        parser._parse_web_link_content.assert_called_once_with(resource)
        transform_web_link_content_to_pdf_mock.assert_called_once_with(web_link_content_mock)
        assert parsed_content == transform_web_link_content_to_pdf_mock.return_value

    @pytest.mark.parametrize(
        "file_suffix",
        [".docx", ".mp3", ".mp4", ".png", ".jpeg", ".ods", ".csv", ".xls", ".pptx", ".txt"],
    )
    def test_parse_webcontent_returns_none_if_resource_file_is_not_pdf(self, file_suffix):
        cartridge_mock = Mock()
        parser = self.parser_type(Mock(), Mock())
        parser._cartridge = cartridge_mock
        web_content_file_mock = Mock()
        resource = {"children": [web_content_file_mock]}

        with patch(
            "cc2olx.content_parsers.pdf.WebContent",
            return_value=Mock(resource_file_path=Mock(suffix=file_suffix)),
        ) as web_content_mock:
            parsed_webcontent = parser._parse_webcontent(resource)

            web_content_mock.assert_called_once_with(cartridge_mock, web_content_file_mock)
            assert parsed_webcontent is None

    @patch(
        "cc2olx.content_parsers.pdf.WebContent",
        return_value=Mock(resource_file_path=Mock(suffix=".pdf"), is_from_web_resources_dir=Mock(return_value=True)),
    )
    def test_parse_webcontent_parses_pdf_from_web_resources_dir(self, web_content_mock):
        parser = self.parser_type(Mock(), Mock())
        cartridge_mock = Mock()
        parse_pdf_webcontent_from_web_resources_dir_mock = Mock()
        parser._cartridge = cartridge_mock
        parser._parse_pdf_webcontent_from_web_resources_dir = parse_pdf_webcontent_from_web_resources_dir_mock
        web_content_file_mock = Mock()
        resource = {"children": [web_content_file_mock]}

        parsed_webcontent = parser._parse_webcontent(resource)

        web_content_mock.assert_called_once_with(cartridge_mock, web_content_file_mock)
        parse_pdf_webcontent_from_web_resources_dir_mock.assert_called_once_with(web_content_mock.return_value)
        assert parsed_webcontent == parse_pdf_webcontent_from_web_resources_dir_mock.return_value

    @patch(
        "cc2olx.content_parsers.pdf.WebContent",
        return_value=Mock(resource_file_path=Mock(suffix=".pdf"), is_from_web_resources_dir=Mock(return_value=False)),
    )
    def test_parse_webcontent_parses_pdf_outside_web_resources_dir(self, web_content_mock):
        parser = self.parser_type(Mock(), Mock())
        cartridge_mock = Mock()
        parse_pdf_webcontent_outside_web_resources_dir_mock = Mock()
        parser._cartridge = cartridge_mock
        parser._parse_pdf_webcontent_outside_web_resources_dir = parse_pdf_webcontent_outside_web_resources_dir_mock
        web_content_file_mock = Mock()
        resource = {"children": [web_content_file_mock]}

        parsed_webcontent = parser._parse_webcontent(resource)

        web_content_mock.assert_called_once_with(cartridge_mock, web_content_file_mock)
        parse_pdf_webcontent_outside_web_resources_dir_mock.assert_called_once_with(web_content_mock.return_value)
        assert parsed_webcontent == parse_pdf_webcontent_outside_web_resources_dir_mock.return_value

    def test_pdf_webcontent_from_web_resources_dir_parsing(self):
        web_content_mock = Mock()
        cartridge_mock = Mock()
        parser = self.parser_type(Mock(), Mock())
        parser._cartridge = cartridge_mock
        expected_content = {"url": web_content_mock.olx_static_path}

        actual_content = parser._parse_pdf_webcontent_from_web_resources_dir(web_content_mock)

        cartridge_mock.olx_to_original_static_file_paths.add_web_resource_path.assert_called_once_with(
            web_content_mock.olx_static_path,
            web_content_mock.resource_file_path,
        )
        assert actual_content == expected_content

    def test_pdf_webcontent_outside_web_resources_dir_parsing(self):
        web_content_mock = Mock()
        cartridge_mock = Mock()
        parser = self.parser_type(Mock(), Mock())
        parser._cartridge = cartridge_mock
        expected_content = {"url": web_content_mock.olx_static_path}

        actual_content = parser._parse_pdf_webcontent_outside_web_resources_dir(web_content_mock)

        cartridge_mock.olx_to_original_static_file_paths.add_extra_path.assert_called_once_with(
            web_content_mock.olx_static_path,
            web_content_mock.resource_relative_path,
        )
        assert actual_content == expected_content

    @pytest.mark.parametrize(
        "web_link_url",
        ["https://example.com/html_content.html", "http://example.com/video.mp4", "/path/to/audio.wav"],
    )
    def test_transform_web_link_content_to_pdf_returns_none_if_web_link_does_not_point_to_pdf_file(self, web_link_url):
        parser = self.parser_type(Mock(), Mock())
        web_link_content = {"href": web_link_url}

        assert parser._transform_web_link_content_to_pdf(web_link_content) is None

    @pytest.mark.parametrize(
        "web_link_url",
        ["https://example.com/PEP_8.pdf", "http://example.com/imscc_profilev1p2-Overview.pdf", "/static/example.pdf"],
    )
    def test_transform_web_link_content_to_pdf_when_web_link_points_to_pdf_file(self, web_link_url):
        parser = self.parser_type(Mock(), Mock())
        web_link_content = {"href": web_link_url}
        expected_content = {"url": web_link_url}

        actual_content = parser._transform_web_link_content_to_pdf(web_link_content)

        assert actual_content == expected_content
