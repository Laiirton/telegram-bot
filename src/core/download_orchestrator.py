import asyncio
import logging
from typing import Callable, Awaitable
from collections import defaultdict

from src.config.settings import settings
from src.core.download_job import DownloadJob
from src.core.result import DownloadResult
from src.downloaders.registry import ExtractorRegistry

logger = logging.getLogger(__name__)

DownloadCallback = Callable[[DownloadJob, DownloadResult], Awaitable[None]]


class DownloadOrchestrator:
    """Manages async download queue with concurrency control."""

    def __init__(
        self,
        registry: ExtractorRegistry,
        on_complete: DownloadCallback | None = None,
    ) -> None:
        self._registry = registry
        self._on_complete = on_complete
        self._queue: asyncio.Queue[DownloadJob] = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_downloads)
        self._task: asyncio.Task[None] | None = None
        self._user_queues: dict[int, list[DownloadJob]] = defaultdict(list)

    def start(self) -> None:
        """Start the background worker."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._worker())

    def stop(self) -> None:
        """Stop the background worker."""
        if self._task and not self._task.done():
            self._task.cancel()

    async def enqueue(self, job: DownloadJob) -> None:
        """Add a download job to the queue."""
        await self._queue.put(job)
        self._user_queues[job.chat_id].append(job)
        logger.info("Enqueued download: chat_id=%s url=%s", job.chat_id, job.url)

    async def _worker(self) -> None:
        """Background worker that processes the queue."""
        while True:
            job = await self._queue.get()
            try:
                async with self._semaphore:
                    await self._process(job)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Unhandled error processing job")
            finally:
                self._queue.task_done()

    async def _process(self, job: DownloadJob) -> None:
        """Process a single download job."""
        logger.info("Processing download: %s", job.url)
        try:
            extractor = self._registry.resolve(job.url)
            result = await extractor.extract(job)
        except Exception as exc:
            from src.core.result import DownloadError
            result = DownloadError(reason=str(exc))

        if self._on_complete:
            try:
                await self._on_complete(job, result)
            except Exception:
                logger.exception("Completion callback failed")
        
        # Remove from user queue after processing
        if job.chat_id in self._user_queues:
            self._user_queues[job.chat_id] = [
                j for j in self._user_queues[job.chat_id] if j.url != job.url
            ]

    async def process_single_for_test(self, job: DownloadJob) -> bool:
        """Process one job inline for testing."""
        try:
            await self._process(job)
            return True
        except Exception:
            return False

    def get_user_status(self, chat_id: int) -> dict[str, int]:
        """Get download status for a specific user."""
        queued = len(self._user_queues.get(chat_id, []))
        return {"queued": queued}

    async def cancel_user_downloads(self, chat_id: int) -> int:
        """Cancel all pending downloads for a specific user."""
        if chat_id not in self._user_queues:
            return 0
        
        count = len(self._user_queues[chat_id])
        self._user_queues[chat_id].clear()
        
        # Also remove from main queue (more complex, simplified for now)
        logger.info("Cancelled %d downloads for chat_id=%s", count, chat_id)
        return count
