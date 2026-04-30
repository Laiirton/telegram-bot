import re
from urllib.parse import urlparse


_URL_RE = re.compile(
    r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*", re.IGNORECASE
)


def find_urls(text: str) -> list[str]:
    """Extract all URLs from a text string."""
    return _URL_RE.findall(text)


def extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return parsed.netloc.lower()
