from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getDepartures import *
from util.bot_src import *

# --- Depart handlers ---
async def handle_depart_start(query, context, data):

    context.user_data["depart_session"]["start"] = data
    name = context.user_data.get("depart_session", {}).get("search_s", {}).get(data, data)
    await query.edit_message_text(
        f"✅ Starting station is set to {name:<20} \nChoose your departure time:",
        reply_markup=build_time_keyboard("depart")
    )

async def handle_depart_time(query, context, data):

    if data == "back":
        context.user_data["depart_session"]["start"] = None
        context.user_data["depart_session"]["search_s"] = {}
        await query.edit_message_text(
            "📍 Choose Your Depature Station.",
            reply_markup=build_location_keyboard("depart", "start")
        )
    else:
        start = context.user_data["depart_session"]["start"]
        await query.edit_message_text(f"🔍 Finding departures from {start}...")
        departures = get_departures("saarvv", start, int(data))
        context.user_data["depart_session"].clear()
        await query.edit_message_text(parse_departures(departures))

async def handle_depart_stations(query, context, data):
    trip_start = context.user_data.get("trip_session", {}).get("start")
    home_start = context.user_data.get("home_session", {}).get("start")
    spawn_start = context.user_data.get("spawn_session", {}).get("start")

    context.user_data["depart_session"]["start"] = "more"

    if spawn_start == "more" or trip_start == "more" or home_start == "more":
        await query.edit_message_text("You had a previous session, resume the search?",reply_markup=build_session_keyboard("depart"))
    else:
        await query.edit_message_text(f"Please Type your keyword to search the station")

async def handle_depart_session(query, context, data):
    if data == "resume":
        context.user_data["depart_session"] = {}
        await query.edit_message_text("Departure search terminated, resume the previous search.\n Please Type your keyword to search the station")
    elif data == "continue":
        context.user_data["trip_session"] = {}
        context.user_data["spawn_session"] = {}
        context.user_data["home_session"] = {}
        context.user_data["depart_session"]["start"] = "more"
        await query.edit_message_text(f"Previous search terminated, continue the departure search.\nPlease Type your keyword to search the station")

async def depart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["depart_session"] = {}
    await update.message.reply_text(
        "📍 Choose Your Depature Station.",
        reply_markup=build_location_keyboard("depart","start")
    )
