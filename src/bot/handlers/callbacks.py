import logging

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from src.bot.handlers.commands import help_command, about_command, status_command

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


def register_callbacks(app) -> None:
    """Register all callback query handlers."""
    app.add_handler(CallbackQueryHandler(button_callback))
