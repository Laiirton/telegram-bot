from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "Olá! Envie um link do TikTok (ou YouTube/Instagram em breve) "
        "que eu baixo o vídeo para você."
    )
