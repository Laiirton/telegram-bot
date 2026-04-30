import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.core.download_orchestrator import DownloadOrchestrator
from src.core.download_job import DownloadJob
from src.utils.url_validator import find_tiktok_urls

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

    orch: DownloadOrchestrator = context.bot_data.get("orchestrator")
    if not orch:
        await update.message.reply_text(
            "❌ *Sistema de downloads indisponível*\n\n"
            "Tente novamente em alguns instantes ou contate o administrador.",
            parse_mode="Markdown",
        )
        return

    count = len(urls)
    # Show typing action and a nicer queue message
    await update.message.reply_chat_action(action="upload_video")

    for idx, url in enumerate(urls, start=1):
        job = DownloadJob(
            chat_id=update.effective_chat.id,
            url=url,
            message_id=update.message.message_id,
        )
        await orch.enqueue(job)
        logger.info("Enqueued URL %d/%d: %s", idx, count, url)

    if count == 1:
        msg = "⏳ *1 vídeo* adicionado à fila!\n\n"
        msg += "Estou baixando... Isso pode levar alguns segundos."
    else:
        msg = f"⏳ *{count} vídeos* adicionados à fila!\n\n"
        msg += "Estou baixando em sequência... Isso pode levar alguns minutos."

    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_to_message_id=update.message.message_id,
    )
