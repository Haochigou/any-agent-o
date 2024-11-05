from enum import Enum


class OutputFormat(str, Enum):
    json = "json"
    markdown = "markdown"
    html = "html"
    yaml = "yaml"