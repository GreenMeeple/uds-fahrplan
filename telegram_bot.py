import os
import re
import unicodedata

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from util.bot_trip import *
from util.bot_depart import *
from util.bot_home import *
from util.bot_spawn import *
from util.getStations import *

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
            case "session":
                await handle_trip_session(query, context, value)
    elif session == "depart":
        match step:
            case "start":
                await handle_depart_start(query, context, value)
            case "more":
                await handle_depart_stations(query, context, value)
            case "time":
                await handle_depart_time(query, context, value)
            case "session":
                await handle_depart_session(query, context, value)
    elif session == "spawn":
        match step:
            case "start":
                await handle_spawn_start(query, context, value) 
            case "more":
                await handle_spawn_stations(query, context, value)
            case "session":
                await handle_spawn_session(query, context, value)
    elif session == "home":
        match step:
            case "start":
                await handle_home_start(query, context, value) 
            case "more":
                await handle_home_stations(query, context, value)
            case "session":
                await handle_home_session(query, context, value)
            case "details":
                await handle_home_details(query, context, value)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    original_input = update.message.text
    user_input = original_input.lower()
    trip_start = context.user_data.get("trip_session", {}).get("start")
    trip_dest = context.user_data.get("trip_session", {}).get("dest")
    depart_start = context.user_data.get("depart_session", {}).get("start")
    spawn_start = context.user_data.get("spawn_session", {}).get("start")
    home_start = context.user_data.get("home_session", {}).get("start")

    print(trip_start, trip_dest, depart_start, spawn_start, home_start)

    more_count = sum(x == "more" for x in [trip_start, trip_dest, depart_start, spawn_start, home_start])

    if more_count == 1:
        stations = getStations(user_input)
        results = parse_stations(stations)
        keyboard = []

        if trip_start == "more":
            for name, lid in results.items(): 
                label = name
                data = lid 
                context.user_data.setdefault("trip_session", {}).setdefault("search_s", {})[data] = label
                trip_start = None
                keyboard.append([InlineKeyboardButton(label, callback_data=f"trip:start:{data}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Select a station:", reply_markup=reply_markup)

        elif trip_dest == "more":
            for name, lid in results.items(): 
                label = name
                data = lid
                trip_dest = None
                context.user_data.setdefault("trip_session", {}).setdefault("search_d", {})[data] = label
                keyboard.append([InlineKeyboardButton(label, callback_data=f"trip:dest:{data}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Select a station:", reply_markup=reply_markup)

        elif depart_start == "more":
            for name, lid in results.items():
                label = name
                data = lid
                depart_start = None
                context.user_data.setdefault("depart_session", {}).setdefault("search_s", {})[data] = label
                keyboard.append([InlineKeyboardButton(label, callback_data=f"depart:start:{data}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Select a station:", reply_markup=reply_markup)

        elif spawn_start == "more":
            for name, lid in results.items():
                label = name
                data = lid
                depart_start = None
                context.user_data.setdefault("spawn_session", {}).setdefault("search_s", {})[data] = label
                keyboard.append([InlineKeyboardButton(label, callback_data=f"spawn:start:{data}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Select a station:", reply_markup=reply_markup)

        elif home_start == "more":
            for name, lid in results.items():
                label = name
                data = lid
                depart_start = None
                context.user_data.setdefault("home_session", {}).setdefault("search_s", {})[data] = label
                keyboard.append([InlineKeyboardButton(label, callback_data=f"home:start:{data}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Select a station:", reply_markup=reply_markup)

        if not results:
            await update.message.reply_text("No matching stations found.")
            return

    else:
        await update.message.reply_text("nah uh")
# --- Run bot ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("depart", depart))
    app.add_handler(CommandHandler("trip", trips))
    app.add_handler(CommandHandler("home", home))
    app.add_handler(CommandHandler("sethome", spawn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🦉 Bot is running.")
    app.run_polling()
