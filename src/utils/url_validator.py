import re
from urllib.parse import urlparse


TIKTOK_URL_RE = re.compile(
    r"https?://(?:www\.|m\.|vm\.|vt\.)?tiktok\.com/[^\s]+",
    re.IGNORECASE,
)

TWITTER_URL_RE = re.compile(
    r"https?://(?:www\.|m\.)?(?:x\.com|twitter\.com)/[^\s]+",
    re.IGNORECASE,
)

VX_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:vxtwitter|fxtwitter|twstalker)\.com/[^\s]+",
    re.IGNORECASE,
)


def find_tiktok_urls(text: str) -> list[str]:
    """Extract TikTok URLs from a text string."""
    return TIKTOK_URL_RE.findall(text)


def find_twitter_urls(text: str) -> list[str]:
    """Extract X.com/Twitter URLs from a text string."""
    return TWITTER_URL_RE.findall(text)


def find_vx_urls(text: str) -> list[str]:
    """Extract vxtwitter/fxtwitter/twstalker URLs from a text string."""
    return VX_URL_RE.findall(text)


def find_supported_urls(text: str) -> list[str]:
    """Extract all supported video URLs (TikTok, X.com, etc.)."""
    urls = []
    urls.extend(TIKTOK_URL_RE.findall(text))
    urls.extend(TWITTER_URL_RE.findall(text))
    urls.extend(VX_URL_RE.findall(text))
    return urls


def extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return parsed.netloc.lower()