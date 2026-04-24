import re
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
_HTML_TAGS = re.compile(r'<[^>]+>')


def sanitize_topic(topic: str) -> str:
    topic = _HTML_TAGS.sub('', topic)
    topic = _CONTROL_CHARS.sub('', topic)
    return topic.strip()
