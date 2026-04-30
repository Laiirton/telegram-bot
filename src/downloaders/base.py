from abc import ABC, abstractmethod
from typing import ClassVar

from src.core.download_job import DownloadJob
from src.core.result import DownloadResult


class BaseExtractor(ABC):
    """Abstract base class for video extractors."""

    DOMAINS: ClassVar[set[str]]

    @abstractmethod
    async def extract(self, job: DownloadJob) -> DownloadResult:
        """Download the video and return a DownloadResult."""
        ...
