from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getDepartures import *
from util.bot_src import *

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
SPAWN_DATA = os.getenv("SPAWN_DATA")

async def handle_spawn_start(query, context, data):
    station = locations[data] if data in locations else data
    name = context.user_data.get("spawn_session", {}).get("search_s", {}).get(data, data)
    user_id = query.from_user.id

    if os.path.exists(SPAWN_DATA):
        with open(SPAWN_DATA, "r") as file:
            try:
                data_list = json.load(file)
            except json.JSONDecodeError:
                data_list = []
    else:
        data_list = []

    # Check if user already exists
    user_found = False
    for entry in data_list:
        if entry["user_id"] == user_id:
            entry["home_id"] = station
            entry["home_name"] = name
            user_found = True
            break

    if not user_found:
        # Add new user entry
        data_list.append({"user_id": user_id, "home": station})

    # Save updated data
    with open(SPAWN_DATA, "w") as file:
        json.dump(data_list, file, indent=2)

    await query.edit_message_text(
        f"✅ User {user_id}, your home is set to {name:<20}")


async def handle_spawn_stations(query, context, data):
    depart_start = context.user_data.get("depart_session", {}).get("start")
    trip_start = context.user_data.get("trip_session", {}).get("start")
    home_start = context.user_data.get("home_session", {}).get("start")

    context.user_data["spawn_session"]["start"] = "more"

    if depart_start == "more" or trip_start == "more" or home_start == "more":
        await query.edit_message_text("You had a previous session, resume the search?",reply_markup=build_session_keyboard("spawn"))
    else:
        await query.edit_message_text(f"Please Type your keyword to search the station")

async def handle_spawn_session(query, context, data):
    if data == "resume":
        context.user_data["spawn_session"] = {}
        await query.edit_message_text("set home search terminated, resume the previous search.\n Please Type your keyword to search the station")
    elif data == "continue":
        context.user_data["depart_session"] = {}
        context.user_data["trip_session"] = {}
        context.user_data["home_session"] = {}
        context.user_data["spawn_session"]["start"] = "more"
        await query.edit_message_text(f"Previous search terminated, continue the set home search.\nPlease Type your keyword to search the station")

async def spawn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["spawn_session"] = {}
    await update.message.reply_text(f"Hello User {update.message.from_user.id}, Set your spawn point",
        reply_markup=build_location_keyboard("spawn","start")
    )
