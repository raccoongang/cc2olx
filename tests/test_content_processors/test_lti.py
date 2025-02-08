from unittest.mock import Mock

from cc2olx.content_processors import LtiContentProcessor


class TestLtiContentProcessor:
    processor_type = LtiContentProcessor

    def test_parsing_results(self, cartridge):
        processor = self.processor_type(cartridge, Mock())

        assert processor._parse("resource_2_lti") == {
            "title": "Learning Tools Interoperability",
            "description": "https://www.imsglobal.org/activity/learning-tools-interoperability",
            "launch_url": "https://lti.local/launch",
            "height": "500",
            "width": "500",
            "custom_parameters": {},
            "lti_id": "learning_tools_interoperability",
        }
