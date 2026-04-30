from dataclasses import dataclass

from src.core.result import VideoQuality


@dataclass(frozen=True, slots=True)
class DownloadJob:
    """Represents a video download request."""
    chat_id: int
    url: str
    message_id: int | None = None
    quality: VideoQuality | None = None
