from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

import pytest

from cc2olx.content_processors import QtiContentProcessor
from cc2olx.content_processors.qti import QtiError


class TestQtiContentProcessor:
    processor_type = QtiContentProcessor

    @pytest.mark.parametrize("cc_profile", ["unknown_profile", "cc.chess.v0p1", "cc.drag_and_drop.v0p1", "123"])
    def test_parse_problem_raises_qti_error_if_cc_profile_is_unknown(self, cc_profile):
        processor = self.processor_type(Mock(), Mock())
        problem_mock = MagicMock(profile=cc_profile)

        with pytest.raises(QtiError) as exc_info:
            processor._parse_problem(problem_mock, Mock(), Mock())

        assert str(exc_info.value) == f'Unknown cc_profile: "{cc_profile}"'

    @patch("cc2olx.content_processors.qti.console_logger")
    def test_parse_problem_logs_inability_to_process_problem(self, console_logger_mock):
        processor = self.processor_type(Mock(), Mock())
        ident_mock = MagicMock()
        resource_file_path_mock = Mock()
        cc_profile_mock = Mock()
        problem_mock = Mock(profile=cc_profile_mock, attrib={"ident": ident_mock})
        expected_logger_info_call_args_list = [
            call("Problem with ID %s can't be converted.", ident_mock),
            call("    Profile %s is not supported.", cc_profile_mock),
            call("    At file %s.", resource_file_path_mock),
        ]

        with patch(
            "cc2olx.content_processors.qti.QtiContentProcessor._problem_parsers_map",
            new_callable=PropertyMock,
        ) as problem_parsers_map_mock:
            problem_parsers_map_mock.return_value = {cc_profile_mock: Mock(side_effect=NotImplementedError)}

            processor._parse_problem(problem_mock, Mock(), resource_file_path_mock)

        assert console_logger_mock.info.call_count == 3
        assert console_logger_mock.info.call_args_list == expected_logger_info_call_args_list

    @pytest.mark.parametrize("cc_profile", ["unknown_profile", "cc.chess.v0p1", "cc.drag_and_drop.v0p1", "123"])
    def test_create_nodes_raises_qti_error_if_cc_profile_is_unknown(self, cc_profile):
        processor = self.processor_type(Mock(), Mock())

        with pytest.raises(QtiError) as exc_info:
            processor._create_nodes([{"cc_profile": cc_profile}])

        assert str(exc_info.value) == f'Unknown cc_profile: "{cc_profile}"'
