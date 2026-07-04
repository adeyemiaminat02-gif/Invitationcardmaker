import os
import logging
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Conversation States
NAME, DATE, TIME, VENUE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("👋 Welcome to the Invitation Maker Bot!\nLet's create your card. What is the **Guest of Honor / Event Name**?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📅 Awesome. What is the **Date** of the event? (e.g., October 12, 2026)")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['date'] = update.message.text
    await update.message.reply_text("⏰ What **Time** does it start? (e.g., 6:00 PM)")
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    await update.message.reply_text("📍 Finally, where is the **Venue**?")
    return VENUE

async def generate_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['venue'] = update.message.text
    await update.message.reply_text("🎨 Generating your unique invitation card... please wait.")

    try:
        # Load your baseline template image
        template_path = "assets/template.png"
        image = Image.open(template_path)
        draw = ImageDraw.Draw(image)

        # Using system default font (You can upload a custom .ttf font file to assets/ if preferred)
        font = ImageFont.load_default()

        # Text data retrieved from conversation
        name_text = f"Join us to celebrate: {context.user_data['name']}"
        details_text = f"Date: {context.user_data['date']} | Time: {context.user_data['time']}"
        venue_text = f"Venue: {context.user_data['venue']}"

        # Draw text on image (Adjust x, y coordinates [e.g., 50, 100] based on your actual template.png layout)
        draw.text((50, 200), name_text, fill="black", font=font)
        draw.text((50, 260), details_text, fill="black", font=font)
        draw.text((50, 320), venue_text, fill="black", font=font)

        # Save to an in-memory byte buffer so we don't clog disk space
        bio = BytesIO()
        bio.name = 'invitation.png'
        image.save(bio, 'PNG')
        bio.seek(0)

        # Send it back to the user
        await update.message.reply_photo(photo=bio, caption="✨ Here is your custom invitation card! 🎉")

    except Exception as e:
        logger.error(f"Error making card: {e}")
        await update.message.reply_text("❌ Something went wrong while generating the card template.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Process cancelled.")
    return ConversationHandler.END

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable missing!")
        return

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Define the stepped conversation wizard
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

    # Use long polling instead of webhooks
    logger.info("Bot started via polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
