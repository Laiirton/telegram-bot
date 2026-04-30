import pytest
from src.utils.url_validator import extract_domain, find_supported_urls, find_tiktok_urls


def test_extract_domain_from_tiktok():
    assert extract_domain("https://vm.tiktok.com/abc123") == "vm.tiktok.com"
    assert extract_domain("https://www.tiktok.com/@user/video/123") == "www.tiktok.com"


def test_extract_domain_invalid():
    with pytest.raises(ValueError):
        extract_domain("not-a-url")


def test_find_urls_finds_multiple():
    text = "Check https://vm.tiktok.com/abc and https://youtube.com/shorts/def"
    urls = find_supported_urls(text)
    assert len(urls) == 1
    assert urls[0] == "https://vm.tiktok.com/abc"


def test_find_urls_empty():
    assert find_supported_urls("no urls here") == []


def test_find_tiktok_urls_finds_variants():
    text = (
        "Links: https://vm.tiktok.com/ZS123 "
        "https://vt.tiktok.com/ZT456 "
        "https://www.tiktok.com/@user/video/789 "
        "https://m.tiktok.com/v/101 "
        "https://tiktok.com/@user/video/112 "
    )
    urls = find_tiktok_urls(text)
    assert len(urls) == 5
    assert urls[0] == "https://vm.tiktok.com/ZS123"
    assert urls[1] == "https://vt.tiktok.com/ZT456"


def test_find_tiktok_urls_with_query_params():
    text = "https://www.tiktok.com/@kitsue__/video/7608920481768443156?is_from_webapp=1&sender_device=pc"
    urls = find_tiktok_urls(text)
    assert len(urls) == 1


def test_find_tiktok_urls_empty():
    assert find_tiktok_urls("no tiktok links here https://youtube.com/abc") == []
