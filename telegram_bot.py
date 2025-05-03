import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from util.bot_src import *

load_dotenv()

# --- Run bot ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("depart", depart))
    app.add_handler(CommandHandler("trip", trips))
    app.add_handler(CommandHandler("home", home))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🦉 Bot is running.")
    app.run_polling()
