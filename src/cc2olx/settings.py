from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

LOG_FORMAT = "{%(filename)s:%(lineno)d} - %(message)s"

# It is used to specify content processors applied to Common Cartridge
# resources. The processors are iterated over in turn, find out whether they
# can process a resource and provide a parsed result if succeeded. The
# iteration is stopped if the processor returns parsed result, otherwise the
# execution flow is passed to the next processor. Thus, the processors' order
# is important: the specific processors should be placed first, the fallback
# ones - at the end.
CONTENT_PROCESSORS = [
    "cc2olx.content_processors.VideoContentProcessor",
    "cc2olx.content_processors.LtiContentProcessor",
    "cc2olx.content_processors.QtiContentProcessor",
    "cc2olx.content_processors.DiscussionContentProcessor",
    "cc2olx.content_processors.HtmlContentProcessor",
]

USE_I18N = False
USE_TZ = False
