import logging

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from src.bot.handlers.commands import help_command, about_command, status_command
from src.core.download_job import DownloadJob
from src.core.download_orchestrator import DownloadOrchestrator

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await help_command(update, context)
    elif query.data == "about":
        await about_command(update, context)
    elif query.data == "status":
        await status_command(update, context)
    elif query.data == "cancel":
        # Simple cancel: send confirmation message
        await query.edit_message_text("🛑 Downloads cancelados.")
    elif query.data == "cancel_quality":
        await query.edit_message_text("❌ Seleção de qualidade cancelada.")
    elif query.data and query.data.startswith("q_"):
        await handle_quality_selection(update, context, query.data[2:])


async def handle_quality_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    option_id: str,
) -> None:
    """Handle quality selection and start download."""
    try:
        quality_options = context.bot_data.get("quality_options", {})
        if option_id not in quality_options:
            await update.callback_query.edit_message_text(
                "❌ Opção de qualidade expirada. Tente enviar o link novamente."
            )
            return
        
        option_data = quality_options[option_id]
        url = option_data["url"]
        quality = option_data["quality"]
        
        # Clean up the option to prevent memory leaks
        del quality_options[option_id]
        
        orch: DownloadOrchestrator = context.bot_data.get("orchestrator")
        if not orch:
            await update.callback_query.edit_message_text(
                "❌ Sistema de downloads indisponível."
            )
            return
        
        chat_id = update.effective_chat.id
        message_id = update.callback_query.message.message_id
        
        job = DownloadJob(
            chat_id=chat_id,
            url=url,
            message_id=message_id,
            quality=quality,
        )
        
        await orch.enqueue(job)
        
        await update.callback_query.edit_message_text(
            f"⏳ *Baixando em {quality.quality_label}...*\n\n"
            f"Isso pode levar alguns segundos.",
            parse_mode="Markdown",
        )
        
        logger.info(
            "Started download for chat_id=%s url=%s quality=%s",
            chat_id,
            url,
            quality.quality_label,
        )
    except Exception as exc:
        logger.exception("Error handling quality selection")
        await update.callback_query.edit_message_text(
            f"❌ Erro ao iniciar download: {str(exc)}"
        )


def register_callbacks(app) -> None:
    """Register all callback query handlers."""
    app.add_handler(CallbackQueryHandler(button_callback))
