from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getDepartures import *
from util.bot_src import *

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
SPAWN_DATA = os.getenv("SPAWN_DATA")

async def handle_home_start(query, context, data):
    start = locations[data] if data in locations else data
    context.user_data["home_session"]["start"] = context.user_data.get("home_session", {}).get("search_s", {}).get(data, data)

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
            dest = entry["home_id"]
            context.user_data["home_session"]["dest"] = entry["home_name"]
            user_found = True
            break
    if not user_found:
        await query.edit_message_text(f"Hello User {user_id}, You haven't set your home station.",
            reply_markup=build_location_keyboard("spawn","start"))

    else:
        await query.edit_message_text(f"🔍 Finding trips from {context.user_data["home_session"]["start"]} to {context.user_data["home_session"]["dest"]}...")
        context.user_data["home_session"]["trip"] = get_trips("saarvv", start, dest, 0)
        trip_basic=parse_trips_basic(context.user_data["home_session"]["trip"], context.user_data["home_session"]["start"], context.user_data["home_session"]["dest"])
        
        if trip_basic is None:
            btn_retry = InlineKeyboardMarkup([[InlineKeyboardButton("again", callback_data="home:details:again")]])
            await query.edit_message_text("❌ No trips found. Try again.", reply_markup=btn_retry)
        else:
            btn_details = InlineKeyboardMarkup([[InlineKeyboardButton("details", callback_data="home:details:show")]])
            await query.edit_message_text(text=trip_basic, reply_markup=btn_details)

async def handle_home_details(query, context, data):
    if data == "again":
        context.user_data["home_session"].clear()
        await query.edit_message_text("🚌 Where do you want to start your journey?",
                                      reply_markup=build_location_keyboard("home","start"))
    else:
        trip = context.user_data["home_session"].get("trip")
        context.user_data["home_session"].clear()
        await query.edit_message_text(text=parse_trips_detail(trip,context.user_data["home_session"]["start"], context.user_data["home_session"]["dest"]))

async def handle_home_stations(query, context, data):
    depart_start = context.user_data.get("depart_session", {}).get("start")
    trip_start = context.user_data.get("trip_session", {}).get("start")
    spawn_start = context.user_data.get("spawn_session", {}).get("start")

    context.user_data["home_session"]["start"] = "more"

    if depart_start == "more" or trip_start == "more" or spawn_start == "more":
        await query.edit_message_text("You had a previous session, resume the search?",reply_markup=build_session_keyboard("home"))
    else:
        await query.edit_message_text(f"Please Type your keyword to search the station")

async def handle_home_session(query, context, data):
    if data == "resume":
        context.user_data["home_session"] = {}
        await query.edit_message_text("home search terminated, resume the previous search.\n Please Type your keyword to search the station")
    elif data == "continue":
        context.user_data["depart_session"] = {}
        context.user_data["trip_session"] = {}
        context.user_data["spawn_session"] = {}
        context.user_data["home_session"]["start"] = "more"
        await query.edit_message_text(f"Previous search terminated, continue the home search.\nPlease Type your keyword to search the station")

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["home_session"] = {}
    user_id = update.message.from_user.id

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
            user_found = True
            break

    if not user_found:
        await update.message.reply_text(f"Hello User {user_id}, You haven't set your home station.",
            reply_markup=build_location_keyboard("spawn","start"))
    else:
        await update.message.reply_text(f"Hello User {user_id}, Where are you right now?",
            reply_markup=build_location_keyboard("home","start"))
