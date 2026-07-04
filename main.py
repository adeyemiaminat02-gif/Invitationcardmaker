import os
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Conversation States
NAME, DATE, TIME, VENUE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("👋 Welcome to the Invitation Maker Bot!\nLet's create your invitation. What is the **Event Name / Guest of Honor**?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📅 What is the **Date** of the event?")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['date'] = update.message.text
    await update.message.reply_text("⏰ What **Time** does it start?")
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    await update.message.reply_text("📍 Where is the **Venue**?")
    return VENUE

async def generate_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['venue'] = update.message.text
    await update.message.reply_text("✍️ Creating your custom invitation text...")

    # Constructing a stylized HTML text invitation
    invitation_template = (
        f"🎉 <b>YOU ARE INVITED!</b> 🎉\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ <b>Event:</b> {context.user_data['name']}\n"
        f"📅 <b>Date:</b> {context.user_data['date']}\n"
        f"⏰ <b>Time:</b> {context.user_data['time']}\n"
        f"📍 <b>Venue:</b> \n<code>{context.user_data['venue']}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f" Hope to see you there! Tap the venue to copy the address easily."
    )

    # Send the formatted message back using ParseMode.HTML
    await update.message.reply_text(text=invitation_template, parse_mode=ParseMode.HTML)
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Process cancelled.")
    return ConversationHandler.END

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN missing!")
        return

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            VENUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_card)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
