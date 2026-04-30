import os
import tempfile
import logging

import yt_dlp

from src.downloaders.base import BaseExtractor
from src.core.download_job import DownloadJob
from src.core.result import DownloadResult, DownloadSuccess, DownloadError, VideoMetadata, VideoQuality
from src.config.settings import settings

logger = logging.getLogger(__name__)

# Path to the cookies file
X_COOKIES_PATH = os.path.join("src", "config", "cookies", "x.com_cookies.txt")


class XExtractor(BaseExtractor):
    """Extractor for X.com (Twitter) videos using yt-dlp."""

    DOMAINS = {
        # Main domains
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
        # Mobile
        "mobile.twitter.com",
        "m.twitter.com",
        # Video embedding services
        "vxtwitter.com",
        "www.vxtwitter.com",
        "fxtwitter.com",
        "www.fxtwitter.com",
        "twstalker.com",
        "www.twstalker.com",
    }

    def _get_ydl_opts(self, extra_opts=None):
        """Generate standard ydl options with cookies support."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": settings.download_timeout,
        }
        
        if os.path.exists(X_COOKIES_PATH):
            opts["cookiefile"] = X_COOKIES_PATH
        else:
            logger.debug(f"Twitter cookies file not found at {X_COOKIES_PATH}. Using unauthenticated requests.")

        if extra_opts:
            opts.update(extra_opts)
        return opts

    async def extract(self, job: DownloadJob) -> DownloadResult:
        try:
            quality = getattr(job, 'quality', None)
            return await self._download(job.url, quality)
        except Exception as exc:
            logger.exception("X.com download failed")
            return DownloadError(reason=str(exc))

    def _get_fallback_urls(self, url: str) -> list[str]:
        """Generate a list of fallback URLs for X.com (Twitter)."""
        fallbacks = []
        for service in ["fxtwitter.com", "vxtwitter.com"]:
            for domain in ["x.com", "twitter.com"]:
                if domain in url:
                    fallbacks.append(url.replace(domain, service))
        return fallbacks

    async def get_metadata(self, url: str) -> VideoMetadata:
        """Extract video metadata without downloading."""
        ydl_opts = self._get_ydl_opts()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except yt_dlp.utils.DownloadError as exc:
                    if "No video could be found" in str(exc):
                        logger.info(f"No video found for {url}, trying fallback URLs")
                        for fallback_url in self._get_fallback_urls(url):
                            try:
                                logger.info(f"Trying fallback: {fallback_url}")
                                info = ydl.extract_info(fallback_url, download=False)
                                break
                            except yt_dlp.utils.DownloadError as e:
                                if "No video could be found" in str(e):
                                    continue
                                raise e
                        else:
                            # All fallbacks failed
                            raise exc
                    else:
                        raise
        except Exception as exc:
            if "No video could be found" in str(exc) or "Este tweet não contém vídeo" in str(exc):
                # This might be a tweet without video
                return VideoMetadata(title="Video", qualities=[], thumbnail=None)
            raise

        title = info.get("title", "Video") or "Video"
        thumbnail = info.get("thumbnail")

        # Extract available qualities: pick best filesize per height
        qualities_dict = {}  # height (int) -> VideoQuality (best filesize)

        for fmt in info.get("formats", []):
            # Skip audio-only formats
            if fmt.get("vcodec") == "none":
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
        tmpdir = tempfile.mkdtemp(prefix="x_dl_")
        try:
            # Build format string based on quality selection
            if quality:
                format_str = quality.format_id
            else:
                format_str = "best[filesize<=" + str(settings.max_file_size_mb) + "M]/best"

            ydl_opts = self._get_ydl_opts({
                "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                "format": format_str,
            })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                except yt_dlp.utils.DownloadError as exc:
                    if "No video could be found" in str(exc):
                        logger.info(f"No video found during download for {url}, trying fallback URLs")
                        for fallback_url in self._get_fallback_urls(url):
                            try:
                                logger.info(f"Trying fallback: {fallback_url}")
                                info = ydl.extract_info(fallback_url, download=True)
                                break
                            except yt_dlp.utils.DownloadError as e:
                                if "No video could be found" in str(e):
                                    continue
                                raise e
                        else:
                            # All fallbacks failed
                            raise exc
                    else:
                        raise
                path = ydl.prepare_filename(info)

            if not os.path.exists(path) or os.path.getsize(path) == 0:
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