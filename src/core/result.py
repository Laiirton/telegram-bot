from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, slots=True)
class DownloadSuccess:
    """Successful download result."""
    path: str
    title: str | None = None


@dataclass(frozen=True, slots=True)
class DownloadError:
    """Failed download result."""
    reason: str


DownloadResult = Union[DownloadSuccess, DownloadError]
