from typing import Callable, List, NamedTuple, Optional, Set

import attrs

from cc2olx.iframe_link_parser import IframeLinkParser


class LinkKeywordProcessor(NamedTuple):
    """
    Encapsulate a link keyword and it's processor.
    """

    keyword: str
    processor: Callable[[str, str], str]


class FibProblemRawAnswers(NamedTuple):
    """
    Encapsulate answers data for a Fill-In-The-Blank problem.
    """

    exact_answers: List[str]
    answer_patterns: List[str]


@attrs.define(frozen=True)
class OlxGeneratorContext:
    """
    Encapsulate an OLX generator context.
    """

    iframe_link_parser: Optional[IframeLinkParser]
    _lti_consumer_ids: Set[str]

    def add_lti_consumer_id(self, lti_consumer_id: str) -> None:
        """
        Populate LTI consumer IDs set with a provided value.
        """
        self._lti_consumer_ids.add(lti_consumer_id)
