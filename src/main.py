import logging
import os
import shutil

from telegram.error import TelegramError

from src.bot.application import build_application
from src.config.settings import settings
from src.core.download_job import DownloadJob
from src.core.result import DownloadSuccess, DownloadError
from src.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


async def _on_download_complete(
    app, job: DownloadJob, result
) -> None:
    """Callback that sends downloaded videos back to Telegram."""
    try:
        if isinstance(result, DownloadSuccess):
            with open(result.path, "rb") as video_file:
                await app.bot.send_video(
                    chat_id=job.chat_id,
                    video=video_file,
                    supports_streaming=True,
                    caption=result.title or "",
                    reply_to_message_id=job.message_id,
                )
            logger.info("Sent video to chat_id=%s", job.chat_id)
            # Clean up temp file and directory
            try:
                os.remove(result.path)
                tmpdir = os.path.dirname(result.path)
                shutil.rmtree(tmpdir, ignore_errors=True)
                logger.info("Cleaned up download: %s", result.path)
            except OSError as exc:
                logger.warning("Failed to clean up download: %s", exc)
        elif isinstance(result, DownloadError):
            await app.bot.send_message(
                chat_id=job.chat_id,
                text=f"Erro ao baixar vídeo: {result.reason}",
                reply_to_message_id=job.message_id,
            )
    except TelegramError as exc:
        logger.error("Telegram error sending result: %s", exc)
    except OSError as exc:
        logger.error("File error sending result: %s", exc)


def main() -> None:
    if not settings.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

    configure_logging()

    app, orch = build_application()

    async def bound_callback(job: DownloadJob, result) -> None:
        await _on_download_complete(app, job, result)

    orch._on_complete = bound_callback

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
