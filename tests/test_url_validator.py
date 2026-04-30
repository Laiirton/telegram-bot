import pytest
from src.utils.url_validator import extract_domain, find_urls


def test_extract_domain_from_tiktok():
    assert extract_domain("https://vm.tiktok.com/abc123") == "vm.tiktok.com"
    assert extract_domain("https://www.tiktok.com/@user/video/123") == "www.tiktok.com"


def test_extract_domain_invalid():
    with pytest.raises(ValueError):
        extract_domain("not-a-url")


def test_find_urls_finds_multiple():
    text = "Check https://vm.tiktok.com/abc and https://youtube.com/shorts/def"
    urls = find_urls(text)
    assert len(urls) == 2
    assert urls[0] == "https://vm.tiktok.com/abc"


def test_find_urls_empty():
    assert find_urls("no urls here") == []
