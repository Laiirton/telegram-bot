from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message with all available commands."""
    text = (
        "📋 *Comandos disponíveis:*\n\n"
        "/start — Iniciar o bot\n"
        "/help — Ver esta mensagem\n"
        "/status — Status dos seus downloads\n"
        "/cancel — Cancelar downloads pendentes\n"
        "/about — Sobre o bot\n\n"
        "*Como usar:*\n"
        "Envie qualquer link de vídeo que eu baixo e envio pra você. "
        "Atualmente suporto: TikTok, e facilmente expansível para outras plataformas.\n\n"
        "_Dica: você pode enviar múltiplos links de uma vez!_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot information."""
    text = (
        "🤖 *Multi-Platform Video Downloader Bot*\n\n"
        "Baixa vídeos de múltiplas plataformas pra você.\n\n"
        "*Tecnologias:*\n"
        "• Python + python-telegram-bot\n"
        "• yt-dlp (download engine)\n"
        "• Arquitetura plug-in (expandível)\n\n"
        "_Criado com 💻 e ☕_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show download status for the user."""
    orch = context.bot_data.get("orchestrator")
    if not orch:
        await update.message.reply_text("❌ Sistema de downloads não disponível.")
        return

    chat_id = update.effective_chat.id
    status = orch.get_user_status(chat_id)
    
    queued = status.get("queued", 0)
    
    if queued == 0:
        text = "✅ *Nenhum download na fila*\n\n"
        text += "Envie um link para começar!"
    else:
        text = f"⏳ *Downloads na fila: {queued}*\n\n"
        text += "Aguarde, estou processando..."
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel all pending downloads for the user."""
    orch = context.bot_data.get("orchestrator")
    if not orch:
        await update.message.reply_text("❌ Sistema de downloads não disponível.")
        return

    chat_id = update.effective_chat.id
    cancelled = await orch.cancel_user_downloads(chat_id)
    
    if cancelled == 0:
        text = "ℹ️ *Nenhum download para cancelar*\n\n"
        text += "Não há downloads pendentes no momento."
    else:
        text = f"🗑️ *{cancelled} download(s) cancelado(s)*\n\n"
        text += "A fila foi limpa."
    
    await update.message.reply_text(text, parse_mode="Markdown")
