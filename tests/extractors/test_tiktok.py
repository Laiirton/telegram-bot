import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.downloaders.extractors.tiktok import TikTokExtractor
from src.core.download_job import DownloadJob
from src.core.result import DownloadSuccess, DownloadError


@pytest.fixture
def extractor():
    return TikTokExtractor()


@pytest.mark.asyncio
async def test_tiktok_extract_success(extractor, tmp_path, monkeypatch):
    job = DownloadJob(chat_id=1, url="https://vm.tiktok.com/abc123")
    fake_path = tmp_path / "video.mp4"
    fake_path.write_bytes(b"fake video")

    mock_info = {"title": "Funny Cat"}

    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        instance = MagicMock()
        instance.extract_info.return_value = mock_info
        instance.prepare_filename.return_value = str(fake_path)
        mock_ydl_cls.return_value.__enter__.return_value = instance

        result = await extractor.extract(job)
        assert isinstance(result, DownloadSuccess)
        assert result.title == "Funny Cat"
        assert result.path == str(fake_path)


@pytest.mark.asyncio
async def test_tiktok_extract_failure(extractor):
    job = DownloadJob(chat_id=1, url="https://vm.tiktok.com/bad")

    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        instance = MagicMock()
        instance.extract_info.side_effect = Exception("Download failed")
        mock_ydl_cls.return_value.__enter__.return_value = instance

        result = await extractor.extract(job)
        assert isinstance(result, DownloadError)
        assert "Download failed" in result.reason


def test_tiktok_domains():
    domains = TikTokExtractor.DOMAINS
    expected = {
        "vm.tiktok.com",
        "vt.tiktok.com",
        "tiktok.com",
        "www.tiktok.com",
        "m.tiktok.com",
        "musical.ly",
    }
    assert domains == expected
