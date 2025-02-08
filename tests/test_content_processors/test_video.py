from unittest.mock import Mock, patch

from cc2olx.content_processors import VideoContentProcessor


class TestVideoContentProcessor:
    processor_type = VideoContentProcessor

    def test_parse_returns_none_if_there_is_no_resource_identifier(self):
        processor = self.processor_type(Mock(), Mock())

        actual_content = processor._parse(None)

        assert actual_content is None

    @patch(
        "cc2olx.content_processors.video.parse_web_link_content",
        Mock(return_value={"href": "youtube.com/watch?v=ABCDeF12345"}),
    )
    def test_parse_parses_youtube_link(self):
        processor = self.processor_type(Mock(), Mock())
        expected_content = {"youtube": "ABCDeF12345"}

        actual_content = processor._parse(Mock())

        assert actual_content == expected_content

    def test_nodes_creation(self):
        processor = self.processor_type(Mock(), Mock())
        expected_video_xml = '<video youtube="1.00:ABCDeF12345" youtube_id_1_0="ABCDeF12345"/>'

        nodes = processor._create_nodes({"youtube": "ABCDeF12345"})

        assert len(nodes) == 1
        assert nodes[0].toxml() == expected_video_xml
