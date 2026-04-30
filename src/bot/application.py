from typing import Callable

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.config.settings import settings
from src.core.download_orchestrator import DownloadOrchestrator, DownloadCallback
from src.downloaders.registry import ExtractorRegistry
from src.downloaders.extractors.tiktok import TikTokExtractor
from src.bot.handlers.start import start
from src.bot.handlers.download import handle_message


def build_application(
    on_complete: DownloadCallback | None = None,
) -> Application:
    """Build and configure the Telegram bot application."""
    registry = ExtractorRegistry()
    registry.register(TikTokExtractor)

    # Future extractors: YouTubeExtractor, InstagramExtractor, etc.
    # registry.register(YouTubeExtractor)

    orch = DownloadOrchestrator(registry, on_complete=on_complete)
    orch.start()

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.bot_data["orchestrator"] = orch
    app.bot_data["registry"] = registry

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
