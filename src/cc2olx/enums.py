from enum import Enum
from typing import Set


class CommonCartridgeResourceType(str, Enum):
    """
    Enumerate Common Cartridge resource types.

    Contain the exact type values and regular expressions to match the type.
    """

    WEB_CONTENT = "webcontent"
    WEB_LINK = r"^imswl_xmlv\d+p\d+$"
    LTI_LINK = r"^imsbasiclti_xmlv\d+p\d+$"
    QTI_ASSESSMENT = r"^imsqti_xmlv\d+p\d+/imscc_xmlv\d+p\d+/assessment$"
    DISCUSSION_TOPIC = r"^imsdt_xmlv\d+p\d+$"
    ASSIGNMENT = r"^assignment_xmlv\d+p\d+$"


class QtiQuestionType(str, Enum):
    """
    Enumerate QTI question types.
    """

    MULTIPLE_CHOICE = "cc.multiple_choice.v0p1"
    MULTIPLE_RESPONSE = "cc.multiple_response.v0p1"
    FILL_IN_THE_BLANK = "cc.fib.v0p1"
    ESSAY = "cc.essay.v0p1"
    BOOLEAN = "cc.true_false.v0p1"
    PATTERN_MATCH = "cc.pattern_match.v0p1"


class AssignmentSubmissionFormatType(str, Enum):
    """
    Enumerate possible submission format types for CC assignments.
    """

    FILE = "file"
    HTML = "html"
    TEXT = "text"
    URL = "url"

    @classmethod
    def get_not_file_types(cls) -> Set["AssignmentSubmissionFormatType"]:
        """
        Provide submission format types except file.
        """
        return {cls.HTML, cls.TEXT, cls.URL}
