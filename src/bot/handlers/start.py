from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with welcome message and quick actions."""
    keyboard = [
        [InlineKeyboardButton("📋 Ver comandos", callback_data="help")],
        [InlineKeyboardButton("📊 Status dos downloads", callback_data="status")],
        [InlineKeyboardButton("ℹ️ Sobre o bot", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 *Olá, {update.effective_user.first_name or 'usuário'}!*\n\n"
        "Sou um bot que baixa vídeos de múltiplas plataformas pra você.\n\n"
        "✨ *Como usar:*\n"
        "Envie qualquer link de vídeo aqui no chat que eu baixo e envio de volta!\n\n"
        "📱 *Plataformas suportadas:*\n"
        "• TikTok (links curtos e normais)\n"
        "• Mais em breve (YouTube, Instagram, etc.)\n\n"
        "_Dica: você pode enviar múltiplos links de uma vez!_",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
