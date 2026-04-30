import os
import tempfile
import logging

import yt_dlp

from src.downloaders.base import BaseExtractor
from src.core.download_job import DownloadJob
from src.core.result import DownloadResult, DownloadSuccess, DownloadError, VideoMetadata, VideoQuality
from src.config.settings import settings

logger = logging.getLogger(__name__)


class TikTokExtractor(BaseExtractor):
    """Extractor for TikTok videos using yt-dlp."""

    DOMAINS = {
        # Shortened / mobile sharing links
        "vm.tiktok.com",
        "vt.tiktok.com",
        # Web domains
        "tiktok.com",
        "www.tiktok.com",
        "m.tiktok.com",
        # Legacy
        "musical.ly",
    }

    async def extract(self, job: DownloadJob) -> DownloadResult:
        try:
            quality = getattr(job, 'quality', None)
            return await self._download(job.url, quality)
        except Exception as exc:
            logger.exception("TikTok download failed")
            return DownloadError(reason=str(exc))

    async def get_metadata(self, url: str) -> VideoMetadata:
        """Extract video metadata without downloading."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": settings.download_timeout,
            "listformats": True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        title = info.get("title", "Video")
        thumbnail = info.get("thumbnail")
        
        # Extract available qualities: pick best filesize per height, filter watermarks
        qualities_dict = {}  # height (int) -> VideoQuality (best filesize)
        
        for fmt in info.get("formats", []):
            # Skip audio-only formats
            if fmt.get("vcodec") == "none":
                continue
            
            # Skip watermarked formats (TikTok watermark)
            format_note = (fmt.get("format_note") or "").lower()
            if "watermark" in format_note or "wm" in format_note:
                continue
            if fmt.get("has_watermark"):
                continue
            
            height = fmt.get("height")
            # Skip formats without height (unknown resolution)
            if height is None:
                continue
            
            width = fmt.get("width")
            ext = fmt.get("ext", "mp4")
            filesize = fmt.get("filesize")
            filesize_mb = filesize / (1024 * 1024) if filesize else None
            
            # Skip if too large
            if filesize_mb and filesize_mb > settings.max_file_size_mb:
                continue
            
            quality_label = f"{height}p"
            
            quality = VideoQuality(
                format_id=fmt.get("format_id", ""),
                quality_label=quality_label,
                ext=ext,
                filesize_mb=round(filesize_mb, 2) if filesize_mb else None,
                height=height,
                width=width,
            )
            
            # Keep the best (largest filesize) for this height
            existing = qualities_dict.get(height)
            if existing is None or (
                quality.filesize_mb is not None and existing.filesize_mb is not None and
                quality.filesize_mb > existing.filesize_mb
            ):
                qualities_dict[height] = quality
        
        qualities = list(qualities_dict.values())
        # Sort by height descending
        qualities.sort(key=lambda q: q.height or 0, reverse=True)
        
        return VideoMetadata(title=title, qualities=qualities, thumbnail=thumbnail)

    async def _download(self, url: str, quality: VideoQuality | None = None) -> DownloadResult:
        # Use mkdtemp so the directory persists until the callback cleans it up
        tmpdir = tempfile.mkdtemp(prefix="tt_dl_")
        try:
            # Build format string based on quality selection
            if quality:
                format_str = quality.format_id
            else:
                format_str = "best[filesize<=" + str(settings.max_file_size_mb) + "M]/best"
            
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                "format": format_str,
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": settings.download_timeout,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)

            if not os.path.exists(path) or os.path.getsize(path) == 0:
                # Try to find the actual file in the directory (yt-dlp may change extension)
                files = [f for f in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, f))]
                if files:
                    path = os.path.join(tmpdir, files[0])
                else:
                    os.rmdir(tmpdir)
                    return DownloadError(reason="Downloaded file is empty or missing")

            return DownloadSuccess(path=path, title=info.get("title"))
        except Exception:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise
