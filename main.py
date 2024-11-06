import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define your Rasa server URL
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f"Hello {user.first_name}! I’m here to assist you. How can I help?")

# Message handler to forward messages to Rasa
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward user messages to Rasa and send back Rasa's response."""
    user_message = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Received message from {user_id}: {user_message}")

    # Send the user's message to the Rasa server
    try:
        response = requests.post(
            RASA_URL,
            json={"sender": str(user_id), "message": user_message}
        )
        response.raise_for_status()
        bot_responses = response.json()

        # Send each response from Rasa back to Telegram
        for bot_response in bot_responses:
            await update.message.reply_text(bot_response.get("text"))

    except requests.exceptions.RequestException as e:
        logger.error(f"Error contacting Rasa: {e}")
        await update.message.reply_text("Извини, я тугодум простите...")

# Main function to set up the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    bot_token = "8076267464:AAE1BizkizmC4YUpJQYvlJVfGh4u4yDZuAs"

    # Set up the application
    application = ApplicationBuilder().token(bot_token).build()

    # Add the command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Add the message handler to process text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
