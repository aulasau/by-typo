import tomllib
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from typography_utils import default_typo

with open("config.toml", "rb") as f:
    token = tomllib.load(f)['bot_token']


async def refine_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_to_process = update.message.text
    clean_text = default_typo.run_typographical_enhancement(text_to_process)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=clean_text)


app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), refine_text))

app.run_polling()
