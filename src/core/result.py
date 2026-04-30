from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, slots=True)
class VideoQuality:
    """Represents a video quality option."""
    format_id: str
    quality_label: str  # e.g., "1080p", "720p"
    ext: str
    filesize_mb: float | None
    height: int | None
    width: int | None


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Metadata extracted from a video URL without downloading."""
    title: str
    qualities: list[VideoQuality]
    thumbnail: str | None = None


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
