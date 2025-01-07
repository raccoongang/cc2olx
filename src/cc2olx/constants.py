OLX_STATIC_DIR = "static"
OLX_STATIC_PATH_TEMPLATE = f"/{OLX_STATIC_DIR}/{{static_filename}}"
WEB_RESOURCES_DIR_NAME = "web_resources"

LINK_HTML = "<a href='{url}'>{text}</a>"
WEB_LINK_NAMESPACE = (
    "http://www.imsglobal.org/xsd/imsccv{major_version}p{minor_version}/imswl_v{major_version}p{minor_version}"
)
YOUTUBE_LINK_PATTERN = r"youtube.com/watch\?v=(?P<video_id>[-\w]+)"
CDATA_PATTERN = r"<!\[CDATA\[(?P<content>.*?)\]\]>"

QTI_RESPROCESSING_TYPES = ["general_fb", "correct_fb", "general_incorrect_fb"]
