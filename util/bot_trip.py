from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getTrips import *
from util.bot_src import *

# --- Trip handlers ---
async def handle_trip_start(query, context, data):
    context.user_data["trip_session"]["start"] = data
    name = context.user_data.get("trip_session", {}).get("search_s", {}).get(data, data)
    await query.edit_message_text(
        f"✅ Starting station is set to {name:<20} \nChoose your departure time:",
        reply_markup=build_time_keyboard("trip")
    )

async def handle_trip_time(query, context, data):

    if data == "back":
        context.user_data["trip_session"]["start"] = None
        context.user_data["trip_session"]["search_s"] = {}
        await query.edit_message_text(
            "🚌 Choose Your Starting Station.",
            reply_markup=build_location_keyboard("trip", "start")
        )
    elif not data.isdigit() or int(data) not in inline_time_options:
        await query.edit_message_text("❗ Please choose a valid time option.", reply_markup=build_time_keyboard("trip"))
        return
    else:
        context.user_data["trip_session"]["time"] = int(data)
        await query.edit_message_text(
            f"✅ Time set.\nChoose Your Destination.",
            reply_markup=build_location_keyboard("trip","dest",context.user_data["trip_session"]["start"])
        )

async def handle_trip_destination(query, context, data):

    if data == "back":
        context.user_data["trip_session"]["time"] = None
        await query.edit_message_text(
            f"✅ Starting station is set to {context.user_data["trip_session"]["start"]:<20} \nChoose your departure time:",
            reply_markup=build_time_keyboard("trip")
        )
    else:
        context.user_data["trip_session"]["dest"] = data
        start_name = context.user_data.get("trip_session", {}).get("search_s", {}).get(data, context.user_data["trip_session"]["start"])
        dest_name = context.user_data.get("trip_session", {}).get("search_d", {}).get(data, data)
        await query.edit_message_text(f"🔍 Finding trips from {start_name} to {dest_name}...")

        context.user_data["trip_session"]["trip"] = get_trips("saarvv", context.user_data["trip_session"]["start"], context.user_data["trip_session"]["dest"], context.user_data["trip_session"]["time"])
        
        trip_basic=parse_trips_basic(context.user_data["trip_session"]["trip"], context.user_data["trip_session"]["start"], context.user_data["trip_session"]["dest"])
        
        if trip_basic is None:
            btn_retry = InlineKeyboardMarkup([[InlineKeyboardButton("again", callback_data="trip:details:again")]])
            await query.edit_message_text("❌ No trips found. Try again.", reply_markup=btn_retry)
        else:
            btn_details = InlineKeyboardMarkup([[InlineKeyboardButton("details", callback_data="trip:details:show")]])
            await query.edit_message_text(text=trip_basic, reply_markup=btn_details)

async def handle_trip_details(query, context, data):
    if data == "again":
        context.user_data["trip_session"].clear()
        await query.edit_message_text("🚌 Where do you want to start your journey?",
                                      reply_markup=build_location_keyboard("trip","start"))
    else:
        trip = context.user_data["trip_session"].get("trip")
        context.user_data["trip_session"].clear()
        await query.edit_message_text(text=parse_trips_detail(trip,context.user_data["trip_session"]["start"], context.user_data["trip_session"]["dest"]))

async def handle_trip_stations(query, context, data):
    depart_start = context.user_data.get("depart_session", {}).get("start")
    home_start = context.user_data.get("home_session", {}).get("start")
    spawn_start = context.user_data.get("spawn_session", {}).get("start")

    context.user_data["trip_session"]["start"] = "more"

    if spawn_start == "more" or depart_start == "more" or home_start == "more":
        await query.edit_message_text("You had a previous session, resume the search?",reply_markup=build_session_keyboard("trip"))
    else:
        await query.edit_message_text(f"Please Type your keyword to search the station")

async def handle_trip_session(query, context, data):
    if data == "resume":
        context.user_data["trip_session"] = {}
        await query.edit_message_text("Trip search terminated, resume the previous search.\n Please Type your keyword to search the station")
    elif data == "continue":
        context.user_data["depart_session"] = {}
        context.user_data["spawn_session"] = {}
        context.user_data["home_session"] = {}
        context.user_data["trip_session"]["start"] = "more"
        await query.edit_message_text(f"Previous search terminated, continue the trip search.\nPlease Type your keyword to search the station")

async def trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["trip_session"] = {}
    
    await update.message.reply_text(
        "🚌 Choose Your Starting Station.",
        reply_markup=build_location_keyboard("trip","start")
    )