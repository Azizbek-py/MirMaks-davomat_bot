import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv

from settings import *
from details.handlers import *

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback_query_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

if __name__ == "__main__":
    print("Pooling ishlayapti...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
