from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.config.settings import settings
from src.core.download_orchestrator import DownloadOrchestrator
from src.downloaders.registry import ExtractorRegistry
from src.downloaders.extractors.tiktok import TikTokExtractor
from src.downloaders.extractors.x_com import XExtractor
from src.bot.handlers.start import start
from src.bot.handlers.download import handle_message
from src.bot.handlers.commands import help_command, about_command, status_command, cancel_command
from src.bot.handlers.callbacks import register_callbacks


def build_application() -> tuple[Application, DownloadOrchestrator]:
    """Build and configure the Telegram bot application."""
    registry = ExtractorRegistry()
    registry.register(TikTokExtractor)
    registry.register(XExtractor)

    # Future extractors: YouTubeExtractor, InstagramExtractor, etc.
    # registry.register(YouTubeExtractor)

    orch = DownloadOrchestrator(registry)

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.bot_data["orchestrator"] = orch
    app.bot_data["registry"] = registry

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("about", about_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callbacks (inline keyboards)
    register_callbacks(app)

    return app, orch
