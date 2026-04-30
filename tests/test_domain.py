import pytest
from src.core.download_job import DownloadJob
from src.core.result import DownloadSuccess, DownloadError


def test_download_job_creation():
    job = DownloadJob(chat_id=123, url="https://vm.tiktok.com/abc")
    assert job.chat_id == 123
    assert job.url == "https://vm.tiktok.com/abc"
    assert job.message_id is None


def test_download_job_with_message_id():
    job = DownloadJob(chat_id=123, url="https://vm.tiktok.com/abc", message_id=456)
    assert job.message_id == 456


def test_download_success():
    r = DownloadSuccess(path="/tmp/video.mp4", title="Cool Video")
    assert r.path == "/tmp/video.mp4"
    assert r.title == "Cool Video"


def test_download_error():
    r = DownloadError(reason="Network unreachable")
    assert r.reason == "Network unreachable"
