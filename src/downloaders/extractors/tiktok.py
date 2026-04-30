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
        "vm.tiktok.com",
        "tiktok.com",
        "www.tiktok.com",
        "m.tiktok.com",
    }

    async def extract(self, job: DownloadJob) -> DownloadResult:
        try:
            return await self._download(job.url)
        except Exception as exc:
            logger.exception("TikTok download failed")
            return DownloadError(reason=str(exc))

    async def _download(self, url: str) -> DownloadResult:
        with tempfile.TemporaryDirectory() as tmpdir:
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
                return DownloadError(reason="Downloaded file is empty or missing")

            return DownloadSuccess(path=path, title=info.get("title"))
