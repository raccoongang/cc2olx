import re
from typing import Dict, Optional, Set, Union

from cc2olx import filesystem
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.enums import AssignmentSubmissionFormatType, CommonCartridgeResourceType
from cc2olx.xml import cc_xml


class AssignmentContentParser(AbstractContentParser):
    """
    Assignment resource content parser.
    """

    DEFAULT_ACCEPTED_FORMAT_TYPES = {AssignmentSubmissionFormatType.HTML, AssignmentSubmissionFormatType.FILE}
    DEFAULT_FILE_UPLOAD_TYPE = "pdf-and-image"
    DEFAULT_WHITE_LISTED_FILE_TYPES = ["pdf", "gif", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"]

    def _parse_content(self, idref: Optional[str]) -> Optional[Dict[str, Union[str, Dict[str, str]]]]:
        if idref:
            if resource := self._cartridge.define_resource(idref):
                if re.match(CommonCartridgeResourceType.ASSIGNMENT, resource["type"]):
                    return self._parse_assignment(resource)
        return None

    def _parse_assignment(self, resource: dict) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Parse the assignment resource.
        """
        resource_file = resource["children"][0]
        tree = filesystem.get_xml_tree(self._cartridge.build_resource_file_path(resource_file.href))
        root = tree.getroot()

        return {
            "title": root.title.text,
            **self._parse_response_data(root),
            **self._parse_prompt_data(root),
        }

    def _parse_prompt_data(self, resource_root: cc_xml.AssignmentElement) -> Dict[str, str]:
        """
        Parse prompt-related data.
        """
        prompt_element = self._define_prompt_element(resource_root)

        return {
            "prompt": getattr(prompt_element, "text", ""),
            "prompts_type": self._define_prompts_type(prompt_element),
        }

    @staticmethod
    def _define_prompt_element(resource_root: cc_xml.AssignmentElement) -> cc_xml.CommonCartridgeElementBase:
        """
        Define the element containing prompt data.
        """
        text = resource_root.get_text()
        return text if text is not None else resource_root.instructor_text

    @staticmethod
    def _define_prompts_type(prompt_element: cc_xml.CommonCartridgeElementBase) -> str:
        """
        Define prompts type.
        """
        raw_prompt_type = prompt_element.attrib["texttype"] if prompt_element is not None else "text/plain"
        return "html" if raw_prompt_type == "text/html" else "text"

    def _parse_response_data(self, resource_root: cc_xml.AssignmentElement) -> dict:
        """
        Parse response-related data.
        """
        accepted_format_types = self._parse_accepted_format_types(resource_root)
        is_file_submission_allowed = AssignmentSubmissionFormatType.FILE in accepted_format_types
        is_textual_submission_allowed = bool(
            AssignmentSubmissionFormatType.get_not_file_types().intersection(accepted_format_types)
        )
        text_response_editor = "tinymce" if AssignmentSubmissionFormatType.HTML in accepted_format_types else "text"

        return {
            "text_response": self._get_text_response(is_textual_submission_allowed, is_file_submission_allowed),
            "text_response_editor": text_response_editor,
            "file_upload_response": (
                self._get_file_upload_response(is_textual_submission_allowed, is_file_submission_allowed)
            ),
            "allow_multiple_files": True,
            "file_upload_type": self.DEFAULT_FILE_UPLOAD_TYPE,
            "white_listed_file_types": self.DEFAULT_WHITE_LISTED_FILE_TYPES,
        }

    def _parse_accepted_format_types(self, resource_root: cc_xml.AssignmentElement) -> Set[str]:
        """
        Parse accepted format types.
        """
        accepted_format_types = {accepted_format.attrib["type"] for accepted_format in resource_root.accepted_formats}
        return accepted_format_types or self.DEFAULT_ACCEPTED_FORMAT_TYPES

    @staticmethod
    def _get_text_response(is_textual_submission_allowed: bool, is_file_submission_allowed: bool) -> str:
        """
        Provide text response necessity option.
        """
        if is_file_submission_allowed:
            return "optional" if is_textual_submission_allowed else ""
        return "required"

    @staticmethod
    def _get_file_upload_response(is_textual_submission_allowed: bool, is_file_submission_allowed: bool) -> str:
        """
        Provide file response necessity option.
        """
        if is_file_submission_allowed:
            return "optional" if is_textual_submission_allowed else "required"
        return ""
