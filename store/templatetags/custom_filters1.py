# custom_filters.py
from django import template
import re

register = template.Library()

@register.filter
def truncate_words(value, num_words=3):
    words = value.split()
    if len(words) > num_words:
        return " ".join(words[:num_words]) + " ..."
    return value


@register.filter
def truncate_title(value, num_words=8):
    words = value.split()
    if len(words) > num_words:
        return " ".join(words[:num_words]) + " ..."
    return value



@register.filter
def truncate_title_blog(value, num_words=10):
    words = value.split()
    if len(words) > num_words:
        return " ".join(words[:num_words]) + " ..."
    return value


@register.filter
def youtube_id(url):
    """
    Extract the YouTube video ID from a URL.
    Supports formats like:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
    """
    # Regex patterns for common YouTube URL formats
    patterns = [
        r'(?:https?://)?(?:www\.)?youtu\.be/([^&?/]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''


