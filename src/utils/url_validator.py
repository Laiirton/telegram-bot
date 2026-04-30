import re
from urllib.parse import urlparse


TIKTOK_URL_RE = re.compile(
    r"https?://(?:www\.|m\.|vm\.|vt\.)?tiktok\.com/[^\s]+",
    re.IGNORECASE,
)

_URL_RE = re.compile(
    r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*", re.IGNORECASE
)


def find_urls(text: str) -> list[str]:
    """Extract all URLs from a text string."""
    return _URL_RE.findall(text)


def find_tiktok_urls(text: str) -> list[str]:
    """Extract TikTok URLs from a text string."""
    return TIKTOK_URL_RE.findall(text)


def extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return parsed.netloc.lower()
