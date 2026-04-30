import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.core.download_orchestrator import DownloadOrchestrator
from src.core.download_job import DownloadJob
from src.utils.url_validator import find_tiktok_urls
from src.downloaders.registry import ExtractorRegistry
from src.bot.handlers.quality import show_quality_options

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages containing video URLs."""
    if not update.message or not update.message.text:
        return

    urls = find_tiktok_urls(update.message.text)
    if not urls:
        await update.message.reply_text(
            "🔍 *Não encontrei nenhum link válido nessa mensagem.*\n\n"
            "Por favor, envie um link de vídeo suportado:\n"
            "• TikTok: `https://vm.tiktok.com/...` ou `https://www.tiktok.com/@usuario/video/...`\n\n"
            "_Em breve adicionarei suporte para mais plataformas!_",
            parse_mode="Markdown",
        )
        return

    registry: ExtractorRegistry = context.bot_data.get("registry")
    if not registry:
        await update.message.reply_text(
            "❌ *Sistema de downloads indisponível*\n\n"
            "Tente novamente em alguns instantes ou contate o administrador.",
            parse_mode="Markdown",
        )
        return

    # For now, handle only the first URL (quality selection is per-video)
    url = urls[0]
    
    # Show typing action while fetching metadata
    await update.message.reply_chat_action(action="typing")
    
    try:
        extractor = registry.resolve(url)
        metadata = await extractor.get_metadata(url)
        
        if not metadata.qualities:
            await update.message.reply_text(
                "❌ *Não foi possível encontrar qualidades disponíveis para este vídeo.*\n\n"
                "O vídeo pode estar privado ou indisponível.",
                parse_mode="Markdown",
            )
            return
        
        await show_quality_options(update, context, url, metadata)
        
        # If there are more URLs, inform the user
        if len(urls) > 1:
            await update.message.reply_text(
                f"ℹ️ *Encontrei {len(urls)} links.*\n\n"
                f"Processando o primeiro. Envie os outros separadamente para escolher a qualidade de cada um.",
                parse_mode="Markdown",
            )
        
    except Exception as exc:
        logger.exception("Error fetching video metadata")
        await update.message.reply_text(
            f"❌ *Erro ao buscar informações do vídeo:*\n`{str(exc)}`",
            parse_mode="Markdown",
        )
