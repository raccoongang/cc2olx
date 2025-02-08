import xml.dom.minidom
from unittest.mock import Mock, patch

from cc2olx.content_processors import DiscussionContentProcessor


class TestDiscussionContentProcessor:
    processor_type = DiscussionContentProcessor

    def test_discussion_content_cleaning_from_cdata(
        self,
        cdata_containing_html,
        expected_cleaned_cdata_containing_html,
    ):
        """
        Test that CDATA cleaning function is called during discussion processing.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        processor = self.processor_type(Mock(), Mock())
        content = {"dependencies": [], "title": Mock(), "text": cdata_containing_html}

        with patch(
            "cc2olx.content_processors.discussion.clean_from_cdata",
            return_value=expected_cleaned_cdata_containing_html,
        ) as clean_from_cdata_mock:
            processor._create_nodes(content)

            clean_from_cdata_mock.assert_called_once()

    def test_discussion_description_is_wrapped_into_cdata(self, cdata_containing_html):
        """
        Test that processed HTML content is wrapped into CDATA section.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
        """
        processor = self.processor_type(Mock(), Mock())
        content = {"dependencies": [], "title": Mock(), "text": cdata_containing_html}

        discussion_description_html, __ = processor._create_nodes(content)

        assert isinstance(discussion_description_html.childNodes[0], xml.dom.minidom.CDATASection)
