import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.core.download_orchestrator import DownloadOrchestrator
from src.core.download_job import DownloadJob
from src.utils.url_validator import find_urls

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages containing video URLs."""
    if not update.message or not update.message.text:
        return

    urls = find_urls(update.message.text)
    if not urls:
        await update.message.reply_text(
            "Não encontrei nenhum link de vídeo. Envie uma URL válida."
        )
        return

    orch: DownloadOrchestrator = context.bot_data["orchestrator"]

    for url in urls:
        job = DownloadJob(
            chat_id=update.effective_chat.id,
            url=url,
            message_id=update.message.message_id,
        )
        await orch.enqueue(job)

    await update.message.reply_text(
        f"{len(urls)} vídeo(s) adicionado(s) à fila de download."
    )
