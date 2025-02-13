import xml.dom.minidom
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import lxml
import pytest

from cc2olx.content_processors import HtmlContentProcessor
from cc2olx.content_processors.dataclasses import ContentProcessorContext
from cc2olx.iframe_link_parser import KalturaIframeLinkParser


class TestHtmlContentProcessor:
    processor_type = HtmlContentProcessor

    def test_parse_returns_default_content_if_there_is_no_resource_identifier(self):
        processor = self.processor_type(Mock(), Mock())
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = processor._parse(None)

        assert actual_content == expected_content

    def test_parse_returns_default_content_if_the_resource_is_missed_in_cartridge(self):
        cartridge_mock = Mock(define_resource=Mock(return_value=None))
        processor = self.processor_type(cartridge_mock, Mock())
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = processor._parse(Mock())

        assert actual_content == expected_content

    @patch("cc2olx.content_processors.html.console_logger")
    def test_parse_logs_missing_resource(self, console_logger_mock):
        cartridge_mock = Mock(define_resource=Mock(return_value=None))
        processor = self.processor_type(cartridge_mock, Mock())
        idref_mock = Mock()

        processor._parse(idref_mock)

        console_logger_mock.info.assert_called_once_with("Missing resource: %s", idref_mock)

    @patch("cc2olx.content_processors.html.parse_web_link_content", Mock(return_value=None))
    @patch(
        "cc2olx.content_processors.html.HtmlContentProcessor.is_known_unprocessed_resource_type",
        Mock(return_value=True),
    )
    def test_parse_returns_default_content_for_known_unprocessed_resource_types(self):
        processor = self.processor_type(MagicMock(), Mock())
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = processor._parse(Mock())

        assert actual_content == expected_content

    @pytest.mark.parametrize(
        "resource_type",
        [
            "imsbasiclti_xmlv1p2",
            "imsbasiclti_xmlv1p3",
            "imsqti_xmlv1p3/imscc_xmlv1p1/assessment",
            "imsqti_xmlv1p3/imscc_xmlv1p3/assessment",
            "imsdt_xmlv1p2",
            "imsdt_xmlv1p3",
        ],
    )
    def test_known_unprocessed_resource_types_is_detected(self, resource_type):
        processor = self.processor_type(Mock(), Mock())

        assert processor.is_known_unprocessed_resource_type(resource_type) is True

    @pytest.mark.parametrize("resource_type", ["imsbasicabc_xmlv1p2", "imsexample_xmlv1p3", "not_cc_type", "imsscorm"])
    def test_not_known_unprocessed_resource_types_is_detected(self, resource_type):
        processor = self.processor_type(Mock(), Mock())

        assert processor.is_known_unprocessed_resource_type(resource_type) is False

    @pytest.mark.parametrize(
        "resource_type",
        ["unsupported_resource_type", "chess_game_xmlv1p1", "drag_and_drop_xmlv1p1", "imsab_xmlv1p2"],
    )
    @patch("cc2olx.content_processors.html.parse_web_link_content", Mock(return_value=None))
    @patch("cc2olx.content_processors.html.HtmlContentProcessor._parse_not_imported_content")
    def test_parse_parses_not_imported_content(self, parse_not_imported_content_mock, resource_type):
        cartridge_mock = Mock(define_resource=Mock(return_value={"type": "imsqti_xmlv1p2"}))
        processor = self.processor_type(cartridge_mock, Mock())

        actual_content = processor._parse(Mock())

        assert actual_content == parse_not_imported_content_mock.return_value

    @patch("cc2olx.content_processors.html.imghdr.what", Mock(return_value=None))
    def test_parse_webcontent_returns_default_content_for_unknown_webcontent_type_from_web_resources_dir(self):
        processor = self.processor_type(
            Mock(build_resource_file_path=Mock(return_value=Path("web_resources/unknown/path/to/file.ext"))),
            Mock(),
        )
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = processor._parse_webcontent(Mock(), MagicMock())

        assert actual_content == expected_content

    @patch("cc2olx.content_processors.html.console_logger")
    @patch("cc2olx.content_processors.html.imghdr.what", Mock(return_value=None))
    def test_parse_webcontent_logs_skipping_webcontent(self, console_logger_mock):
        resource_file_path = Path("web_resources/unknown/path/to/file.ext")
        processor = self.processor_type(Mock(build_resource_file_path=Mock(return_value=resource_file_path)), Mock())

        processor._parse_webcontent(Mock(), MagicMock())

        console_logger_mock.info.assert_called_once_with("Skipping webcontent: %s", resource_file_path)

    @patch("cc2olx.content_processors.html.console_logger")
    @patch("cc2olx.content_processors.html.open", Mock(side_effect=FileNotFoundError))
    def test_webcontent_html_file_reading_failure_is_logged(self, console_logger_mock):
        processor = self.processor_type(Mock(), Mock())
        idref_mock = Mock()
        resource_file_path_mock = Mock()

        with pytest.raises(FileNotFoundError):
            processor._parse_webcontent_html_file(idref_mock, resource_file_path_mock)

        console_logger_mock.error.assert_called_once_with(
            "Failure reading %s from id %s",
            resource_file_path_mock,
            idref_mock,
        )

    @pytest.mark.parametrize(
        "resource,message",
        [
            (
                {"type": "some_type_mock", "href": "https://example.com/some/type/link/"},
                "Not imported content: type = 'some_type_mock', href = 'https://example.com/some/type/link/'",
            ),
            ({"type": "some_type_mock"}, "Not imported content: type = 'some_type_mock'"),
        ],
    )
    @patch("cc2olx.content_processors.html.console_logger")
    def test_not_imported_content_parsing_with_href_in_resource(self, console_logger_mock, resource, message):
        processor = self.processor_type(Mock(), Mock())
        expected_content = {"html": message}

        actual_content = processor._parse_not_imported_content(resource)

        console_logger_mock.info.assert_called_once_with("%s", message)
        assert actual_content == expected_content

    def test_parsing_results(self, cartridge):
        processor = self.processor_type(cartridge, Mock())

        assert processor._parse("resource_1_course") == {
            "html": "Not imported content: type = 'associatedcontent/imscc_xmlv1p1/learning-application-resource', "
            "href = 'course_settings/canvas_export.txt'"
        }

        assert processor._parse("resource_3_vertical") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_3_vertical"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<img src="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg" alt="fractal.jpg"'
            ' width="500" height="375" />\n'
            "<p>Fractal Image <a "
            'href="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg?canvas_download=1" '
            'target="_blank">Fractal Image</a></p>\n'
            "</body>\n</html>\n"
        }

        assert processor._parse("resource_6_wiki_content") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_6_wiki_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24WIKI_REFERENCE%24/pages/wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        }

        assert processor._parse("resource_7_canvas_content") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_7_canvas_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24CANVAS_OBJECT_REFERENCE%24/quizzes/abc">Canvas Content</a>'
            "\n</body>\n</html>\n"
        }

        assert processor._parse("resource_module-|-introduction") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_module-|-introduction"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24WIKI_REFERENCE%24/pages/wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        }

    def test_process_html_for_iframe_provides_video_blocks(self, iframe_content, link_map_csv):
        context = ContentProcessorContext(
            iframe_link_parser=KalturaIframeLinkParser(link_map_csv),
            lti_consumer_ids=set(),
            relative_links_source=None,
        )
        processor = self.processor_type(Mock(), context)

        _, video_olx = processor._process_html_for_iframe(iframe_content)

        assert len(video_olx) == 1
        assert video_olx[0].nodeName == "video"

    def test_process_html_for_iframe_removes_iframes_from_html(self, iframe_content, link_map_csv):
        context = ContentProcessorContext(
            iframe_link_parser=KalturaIframeLinkParser(link_map_csv),
            lti_consumer_ids=set(),
            relative_links_source=None,
        )
        processor = self.processor_type(Mock(), context)

        html_str, _ = processor._process_html_for_iframe(iframe_content)

        html = lxml.html.fromstring(html_str)
        iframe = html.xpath("//iframe")
        assert len(iframe) == 0

    def test_html_cleaning_from_cdata(self, cdata_containing_html, expected_cleaned_cdata_containing_html):
        """
        Test that CDATA cleaning function is called during HTML processing.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            relative_links_source=None,
        )
        processor = self.processor_type(Mock(), context)
        content = {"html": cdata_containing_html}

        with patch(
            "cc2olx.content_processors.html.clean_from_cdata",
            return_value=expected_cleaned_cdata_containing_html,
        ) as clean_from_cdata_mock:
            processor._create_nodes(content)

            clean_from_cdata_mock.assert_called_once()

    def test_processed_html_content_is_wrapped_into_cdata(self, cdata_containing_html):
        """
        Test that processed HTML content is wrapped into CDATA section.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
        """
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            relative_links_source=None,
        )
        processor = self.processor_type(Mock(), context)
        content = {"html": cdata_containing_html}

        result_html, *__ = processor._create_nodes(content)

        assert isinstance(result_html.childNodes[0], xml.dom.minidom.CDATASection)
