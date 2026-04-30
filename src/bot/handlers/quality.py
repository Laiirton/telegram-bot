import logging
import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.core.result import VideoQuality, VideoMetadata
from src.downloaders.registry import ExtractorRegistry

logger = logging.getLogger(__name__)


async def show_quality_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str,
    metadata: VideoMetadata,
) -> None:
    """Show quality selection keyboard to user."""
    keyboard = []
    
    # Store quality options in bot_data with unique IDs
    if "quality_options" not in context.bot_data:
        context.bot_data["quality_options"] = {}
    
    # Create buttons for each quality
    for quality in metadata.qualities:
        size_str = f"{quality.filesize_mb} MB" if quality.filesize_mb else "Tamanho desconhecido"
        button_text = f"🎬 {quality.quality_label} ({size_str})"
        
        # Generate unique ID and store quality data
        option_id = str(uuid.uuid4())[:8]
        context.bot_data["quality_options"][option_id] = {
            "url": url,
            "quality": quality,
        }
        
        callback_data = f"q_{option_id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Add cancel button
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel_quality")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"📹 *{metadata.title}*\n\n"
        f"Selecione a qualidade desejada:\n"
        f"Total de {len(metadata.qualities)} opções disponíveis."
    )
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
