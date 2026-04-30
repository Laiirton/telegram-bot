import pytest
from unittest.mock import AsyncMock, patch
from src.downloaders.base import BaseExtractor
from src.downloaders.registry import ExtractorRegistry
from src.core.download_job import DownloadJob
from src.core.result import DownloadSuccess


class FakeExtractor(BaseExtractor):
    DOMAINS = {"example.com"}

    async def extract(self, job: DownloadJob) -> DownloadSuccess:
        return DownloadSuccess(path="/fake", title="Fake")

    async def get_metadata(self, url: str):
        return None


def test_registry_registration():
    reg = ExtractorRegistry()
    reg.register(FakeExtractor)
    extractor = reg.resolve("https://example.com/video/1")
    assert isinstance(extractor, FakeExtractor)


def test_registry_no_match():
    reg = ExtractorRegistry()
    reg.register(FakeExtractor)
    with pytest.raises(ValueError):
        reg.resolve("https://unknown.com/1")
