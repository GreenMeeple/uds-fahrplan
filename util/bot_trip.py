from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getTrips import *
from util.bot_src import *

# --- Trip handlers ---
async def handle_trip_start(query, context, data):
    if data not in locations:
        await query.edit_message_text("🚌 Where do you want to start your journey?", reply_markup=build_location_keyboard("trip","start"))
        return
    context.user_data["trip_session"]["start"] = data
    await query.edit_message_text(
        f"✅ Starting point set to {data}.\n\nChoose your departure time:",
        reply_markup=build_time_keyboard("trip")
    )

async def handle_trip_time(query, context, data):
    if not data.isdigit() or int(data) not in inline_time_options:
        await query.edit_message_text("❗ Please choose a valid time option.", reply_markup=build_time_keyboard("trip"))
        return
    context.user_data["trip_session"]["time"] = int(data)
    await query.edit_message_text(
        f"✅ Time set to {data} min later.\n\nNow, where do you want to go?",
        reply_markup=build_location_keyboard("trip","dest",context.user_data["trip_session"]["start"])
    )

async def handle_trip_destination(query, context, data):

    context.user_data["trip_session"]["destination"] = data
    await query.edit_message_text(f"🔍 Finding trips from {context.user_data["trip_session"]["start"]} to {context.user_data["trip_session"]["destination"]}...")

    context.user_data["trip_session"]["trip"] = get_trips("saarvv", context.user_data["trip_session"]["start"], context.user_data["trip_session"]["destination"], context.user_data["trip_session"]["time"])
    try:
        trip_basic=parse_trips_basic(context.user_data["trip_session"]["trip"])
    except:
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
        await query.edit_message_text(text=parse_trips_detail(trip))

async def handle_trip_stations(query, context, data):
    if data not in locations:
        await query.edit_message_text("🚌 Where do you want to start your journey?", reply_markup=build_location_keyboard("trip","start"))
        return
    context.user_data.setdefault("trip_session", {})["start"] = data
    await query.edit_message_text(
        f"✅ Starting point set to {data}.\n\nChoose your departure time:",
        reply_markup=build_time_keyboard("trip")
    )


async def trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["trip_session"] = {}
    await update.message.reply_text(
        "🚌 Where do you want to start your journey?",
        reply_markup=build_location_keyboard("trip","start")
    )