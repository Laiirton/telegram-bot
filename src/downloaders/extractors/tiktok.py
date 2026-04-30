import os
import tempfile
import logging

import yt_dlp

from src.downloaders.base import BaseExtractor
from src.core.download_job import DownloadJob
from src.core.result import DownloadResult, DownloadSuccess, DownloadError
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
            return await self._download(job.url)
        except Exception as exc:
            logger.exception("TikTok download failed")
            return DownloadError(reason=str(exc))

    async def _download(self, url: str) -> DownloadResult:
        # Use mkdtemp so the directory persists until the callback cleans it up
        tmpdir = tempfile.mkdtemp(prefix="tt_dl_")
        try:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                "format": "best[filesize<=" + str(settings.max_file_size_mb) + "M]/best",
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
