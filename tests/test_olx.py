import json
import xml.dom.minidom
from unittest.mock import Mock, call, patch

import pytest

from cc2olx import olx
from cc2olx.content_processors import HtmlContentProcessor
from .utils import format_xml


def test_olx_export_xml(cartridge, link_map_csv, studio_course_xml, relative_links_source):
    xml = olx.OlxExport(cartridge, link_map_csv, relative_links_source=relative_links_source).xml()

    assert format_xml(xml) == format_xml(studio_course_xml)


def test_olx_export_wiki_page_disabled(cartridge, link_map_csv, studio_course_xml):
    policy_json = olx.OlxExport(cartridge, link_map_csv).policy()
    policy = json.loads(policy_json)
    tabs = policy["course/course"]["tabs"]

    for tab in tabs:
        if tab["name"] == "Wiki":
            assert tab["is_hidden"]


def test_resource_processing_by_content_processor_failure_is_logged():
    file_not_found_error = FileNotFoundError("The requested file was not found.")
    invalid_name_error = Exception("Invalid name.")
    html_processor_mock = Mock(process=Mock(side_effect=file_not_found_error))
    lti_processor_mock = Mock(process=Mock(side_effect=invalid_name_error))
    content_processors_mock = [
        Mock(process=Mock(return_value=None)),
        html_processor_mock,
        lti_processor_mock,
        Mock(),
    ]
    idref_mock = Mock()
    element_data = {"identifierref": idref_mock}
    olx_export = olx.OlxExport(Mock())
    olx_export._content_processors = content_processors_mock
    olx_export._log_resource_processing_by_content_processor_failure = Mock()
    expected_log_resource_processing_by_content_processor_failure_call_args_list = [
        call(idref_mock, html_processor_mock, file_not_found_error),
        call(idref_mock, lti_processor_mock, invalid_name_error),
    ]

    olx_export._create_olx_nodes(element_data)

    assert olx_export._log_resource_processing_by_content_processor_failure.call_count == 2
    assert (
        olx_export._log_resource_processing_by_content_processor_failure.call_args_list
        == expected_log_resource_processing_by_content_processor_failure_call_args_list
    )


def test_olx_export_exception_is_raised_when_no_content_processor_created_olx_nodes():
    content_processors_mock = [Mock(process=Mock(return_value=None)) for _ in range(5)]
    element_data = {"identifierref": "id_1"}
    olx_export = olx.OlxExport(Mock())
    olx_export._content_processors = content_processors_mock

    with pytest.raises(olx.OlxExportException) as exc_info:
        olx_export._create_olx_nodes(element_data)

    assert str(exc_info.value) == "The resource with 'id_1' identifier value is not supported."


def test_nodes_creation_failure_is_logged_during_olx_nodes_adding():
    idref_mock = Mock()
    olx_export_error = olx.OlxExportException(f"The resource with {idref_mock!r} identifier value is not supported.")
    olx_export = olx.OlxExport(Mock())
    olx_export._log_nodes_creation_failure = Mock()
    olx_export._create_olx_nodes = Mock(side_effect=olx_export_error)
    course_data = [{"identifierref": idref_mock}]

    olx_export._add_olx_nodes(Mock(), course_data, [])

    olx_export._log_nodes_creation_failure.assert_called_once_with(idref_mock, olx_export_error)


@patch("cc2olx.content_processors.html.build_input_processing_file_logger", Mock())
@patch("cc2olx.olx.build_default_exception_output")
@patch("cc2olx.olx.console_logger")
def test_resource_processing_by_content_processor_failure_logging(
    console_logger_mock,
    build_default_exception_output_mock,
):
    olx_export = olx.OlxExport(Mock())
    olx_export._file_logger = Mock()
    idref_mock = Mock()
    exception = FileNotFoundError()
    content_processor = HtmlContentProcessor(Mock(), Mock())
    expected_console_logger_error_call_args_list = [
        call(
            'An error occurred during resource "%s" processing by %s:',
            idref_mock,
            "HtmlContentProcessor",
        ),
        call("The processor is skipped."),
    ]

    olx_export._log_resource_processing_by_content_processor_failure(idref_mock, content_processor, exception)

    assert console_logger_mock.error.call_count == 2
    assert console_logger_mock.error.call_args_list == expected_console_logger_error_call_args_list
    console_logger_mock.exception.assert_called_once_with(exception)
    build_default_exception_output_mock.assert_called_once_with(exception)
    olx_export._file_logger.error.assert_called_once_with(
        'An error occurred during resource "%s" processing by %s: "%s". The processor is skipped.',
        idref_mock,
        "HtmlContentProcessor",
        build_default_exception_output_mock.return_value,
    )


@patch("cc2olx.olx.build_default_exception_output")
@patch("cc2olx.olx.console_logger")
def test_nodes_creation_failure_logging(console_logger_mock, build_default_exception_output_mock):
    olx_export = olx.OlxExport(Mock())
    olx_export._file_logger = Mock()
    idref_mock = Mock()
    exception = olx.OlxExportException(f"The resource with {idref_mock!r} identifier value is not supported.")

    olx_export._log_nodes_creation_failure(idref_mock, exception)

    console_logger_mock.error.assert_called_once_with(
        'An error occurred during the resource with "%s" identifier processing:',
        idref_mock,
    )
    console_logger_mock.exception.assert_called_once_with(exception)
    build_default_exception_output_mock.assert_called_once_with(exception)
    olx_export._file_logger.error.assert_called_once_with(
        'An error occurred during the resource with "%s" identifier processing: "%s".',
        idref_mock,
        build_default_exception_output_mock.return_value,
    )


class TestOlxExporterLtiPolicy:
    def _get_oxl_exporter(self, cartridge, passports_csv):
        """
        Helper function to create olx exporter.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.

        Returns:
            [OlxExport]: OlxExport instance.
        """
        olx_exporter = olx.OlxExport(cartridge, passport_file=passports_csv)
        olx_exporter.doc = xml.dom.minidom.Document()
        return olx_exporter

    def test_lti_consumer_ids_are_defined(self, cartridge, passports_csv):
        olx_exporter = self._get_oxl_exporter(cartridge, passports_csv)
        _ = olx_exporter.xml()

        assert olx_exporter.lti_consumer_ids == {"external_tool_lti", "learning_tools_interoperability"}

    def test_policy_contains_advanced_module(self, cartridge, passports_csv, caplog):
        olx_exporter = self._get_oxl_exporter(cartridge, passports_csv)
        _ = olx_exporter.xml()
        caplog.clear()
        policy = json.loads(olx_exporter.policy())

        assert policy["course/course"]["advanced_modules"] == ["lti_consumer"]
        # Converting to set because the order might change
        assert set(policy["course/course"]["lti_passports"]) == {
            "codio:my_codio_key:my_codio_secret",
            "lti_tool:my_consumer_key:my_consumer_secret_key",
            "external_tool_lti:external_tool_lti_key:external_tool_lti_secret",
            "learning_tools_interoperability:consumer_key:consumer_secret",
        }

        # Warning for missing LTI passort is logged
        assert ["Missing LTI Passport for learning_tools_interoperability. Using default."] == [
            rec.message for rec in caplog.records
        ]
