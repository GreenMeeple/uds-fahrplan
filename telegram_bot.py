import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from util.bot_trip import *
from util.bot_depart import *

load_dotenv()

# --- Callback handler ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        session, step, value = query.data.split(":", 2)
        print(session, step, value)
    except Exception as e:
        print(f"⚠️ Callback parse error: {e}")
        return

    # Ensure session dicts
    context.user_data.setdefault("trip_session", {})
    context.user_data.setdefault("depart_session", {})

    if session == "trip":
        match step:
            case "start":
                await handle_trip_start(query, context, value)
            case "more":
                await handle_trip_stations(query, context, value)
            case "time":
                await handle_trip_time(query, context, value)
            case "dest":
                await handle_trip_destination(query, context, value)
            case "details":
                await handle_trip_details(query, context, value)
    elif session == "depart":
        match step:
            case "start":
                await handle_depart_start(query, context, value)
            case "time":
                await handle_depart_time(query, context, value)
    elif session == "home":
        await query.edit_message_text("🏠 Home page. Use /trip or /depart")

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
