import xml.dom.minidom
from typing import Dict, List

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.olx_generators.utils import generate_default_ora_criteria
from cc2olx.utils import element_builder


class AssignmentOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for assignments.
    """

    FILE_UPLOAD_TYPE = "pdf-and-image"
    WHITE_LISTED_FILE_TYPES = ["pdf", "gif", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"]

    def create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        el = element_builder(self._doc)

        ora = el(
            "openassessment",
            [
                el("title", content["title"]),
                el("assessments", [
                    el(
                        "assessment",
                        None,
                        {"name": "staff-assessment", "required": "True"}
                    )
                ]),
                el("prompts", [
                    el("prompt", [
                        el("description", content["prompt"])
                    ])
                ]),
                el("rubric", [
                    *generate_default_ora_criteria(),
                    el(
                        "feedbackprompt",
                        "(Optional) What aspects of this response stood out to you? What did it do well? How could it "
                        "be improved?",
                    ),
                    el("feedback_default_text", "I think that this response..."),
                ])
            ],
            self._generate_openassessment_attributes(content),
        )

        return [ora]

    @staticmethod
    def _generate_openassessment_attributes(content: dict) -> Dict[str, str]:
        """
        Generate ORA root tag attributes.
        """
        return {
            "prompts_type": content["prompts_type"],
            "text_response_editor": content["text_response_editor"],
            "text_response": content["text_response"],
            "file_upload_response": content["file_upload_response"],
            "file_upload_type": content["file_upload_type"],
            "white_listed_file_types": ",".join(content["white_listed_file_types"]),
            "allow_multiple_files": str(content["allow_multiple_files"]),
        }
