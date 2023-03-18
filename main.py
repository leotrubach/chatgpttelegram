import os
from collections import defaultdict
import logging
import openai
import dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

dotenv.load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

openai.api_key = os.getenv("OPENAI_API_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_HISTORY = defaultdict(list)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_HISTORY[update.effective_chat.id] = []


async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    item = {
        "role": "user", 
        "content": message
    }
    messages=[
        *CHAT_HISTORY[update.effective_chat.id],
        item
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages,
    )
    bot_item = response["choices"][0]["message"]
    answer = bot_item["content"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
    CHAT_HISTORY[update.effective_chat.id].append(item)
    CHAT_HISTORY[update.effective_chat.id].append(bot_item)
    print(CHAT_HISTORY)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    reset_handler = CommandHandler('reset', reset)
    application.add_handler(reset_handler)
    
    message_handler = MessageHandler(None, default_handler)
    application.add_handler(message_handler)

    application.run_polling()