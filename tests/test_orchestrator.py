import pytest
from unittest.mock import AsyncMock, patch
from src.core.download_orchestrator import DownloadOrchestrator
from src.core.download_job import DownloadJob
from src.core.result import DownloadSuccess
from src.downloaders.registry import ExtractorRegistry
from src.downloaders.extractors.tiktok import TikTokExtractor


@pytest.fixture
def registry():
    reg = ExtractorRegistry()
    reg.register(TikTokExtractor)
    return reg


@pytest.mark.asyncio
async def test_process_single(registry, monkeypatch):
    orch = DownloadOrchestrator(registry)
    job = DownloadJob(chat_id=1, url="https://vm.tiktok.com/abc")

    mock_result = DownloadSuccess(path="/tmp/vid.mp4", title="Test")

    with patch.object(TikTokExtractor, "extract", new_callable=AsyncMock, return_value=mock_result):
        result = await orch.process_single_for_test(job)
        assert result is True


@pytest.mark.asyncio
async def test_enqueue(registry):
    orch = DownloadOrchestrator(registry)
    job = DownloadJob(chat_id=1, url="https://vm.tiktok.com/abc")
    await orch.enqueue(job)
    assert orch._queue.qsize() == 1
