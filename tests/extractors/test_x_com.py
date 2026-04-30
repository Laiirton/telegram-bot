import pytest
from unittest.mock import patch, MagicMock

from src.downloaders.extractors.x_com import XExtractor
from src.core.download_job import DownloadJob
from src.core.result import DownloadSuccess, DownloadError


@pytest.fixture
def extractor():
    return XExtractor()


def test_x_domains():
    """XExtractor should support twitter/x domains."""
    domains = XExtractor.DOMAINS
    assert "x.com" in domains
    assert "twitter.com" in domains
    assert "www.x.com" in domains
    assert "www.twitter.com" in domains
    assert "vxtwitter.com" in domains
    assert "fxtwitter.com" in domains


@pytest.mark.asyncio
async def test_x_extract_success(extractor, tmp_path):
    job = DownloadJob(chat_id=1, url="https://x.com/user/status/123")
    fake_path = tmp_path / "video.mp4"
    fake_path.write_bytes(b"fake video")

    mock_info = {"title": "Test Video"}

    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        instance = MagicMock()
        instance.extract_info.return_value = mock_info
        instance.prepare_filename.return_value = str(fake_path)
        mock_ydl_cls.return_value.__enter__.return_value = instance

        result = await extractor.extract(job)
        assert isinstance(result, DownloadSuccess)
        assert result.title == "Test Video"
        assert result.path == str(fake_path)


@pytest.mark.asyncio
async def test_x_extract_failure(extractor):
    job = DownloadJob(chat_id=1, url="https://x.com/user/status/bad")

    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        instance = MagicMock()
        instance.extract_info.side_effect = Exception("Download failed")
        mock_ydl_cls.return_value.__enter__.return_value = instance

        result = await extractor.extract(job)
        assert isinstance(result, DownloadError)
        assert "Download failed" in result.reason