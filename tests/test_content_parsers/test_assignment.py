from unittest.mock import Mock

import pytest

from cc2olx.content_parsers import AssignmentContentParser


class TestAssignmentContentParser:
    @pytest.mark.parametrize(
        "is_textual_submission_allowed,is_file_submission_allowed,expected_text_response",
        [
            (True, True, "optional"),
            (True, False, "required"),
            (False, True, ""),
            (False, False, "required"),
        ]
    )
    def test_get_text_response_results(
        self,
        is_textual_submission_allowed,
        is_file_submission_allowed,
        expected_text_response,
    ):
        parser = AssignmentContentParser(Mock())

        actual_text_response = parser._get_text_response(is_textual_submission_allowed, is_file_submission_allowed)

        assert actual_text_response == expected_text_response

    @pytest.mark.parametrize(
        "is_textual_submission_allowed,is_file_submission_allowed,expected_text_response",
        [
            (True, True, "optional"),
            (True, False, ""),
            (False, True, "required"),
            (False, False, ""),
        ]
    )
    def test_get_file_upload_response_results(
        self,
        is_textual_submission_allowed,
        is_file_submission_allowed,
        expected_text_response,
    ):
        parser = AssignmentContentParser(Mock())

        actual_text_response = parser._get_file_upload_response(
            is_textual_submission_allowed,
            is_file_submission_allowed,
        )

        assert actual_text_response == expected_text_response
