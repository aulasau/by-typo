import sys
import tomllib
import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from typography_utils import default_typo

logger = logging.getLogger('by-typo-front')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


with open("config.toml", "rb") as f:
    token = tomllib.load(f)['bot_token']


async def refine_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_to_process = update.message.text
    clean_text = default_typo.run_typographical_enhancement(text_to_process)
    logger.info(f'\nInitial text:\n{text_to_process}\n\n---------\nCleaned text:\n{clean_text}\n************\n************\n')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=clean_text)


app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), refine_text))

app.run_polling()
