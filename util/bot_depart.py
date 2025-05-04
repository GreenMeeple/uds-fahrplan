from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getDepartures import *
from util.bot_src import *

# --- Depart handlers ---
async def handle_depart_start(query, context, data):
    if data not in locations:
        await query.edit_message_text("📍 Which station do you want to see departures for?", reply_markup=build_location_keyboard("depart","start"))
        return
    context.user_data.setdefault("depart_session", {})["start"] = data
    await query.edit_message_text(
        f"✅ Station set to {data}. Choose departure time:",
        reply_markup=build_time_keyboard("depart")
    )

async def handle_depart_time(query, context, data):
    start = context.user_data["depart_session"]["start"]
    await query.edit_message_text(f"🔍 Finding departures from {start}...")
    departures = get_departures("saarvv", start, int(data))
    context.user_data["depart_session"].clear()
    await query.edit_message_text(parse_departures(departures))

async def depart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["depart_session"] = {}
    await update.message.reply_text(
        "📍 Which station do you want to see departures for?",
        reply_markup=build_location_keyboard("depart","start")
    )

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["home_session"] = {}
    await update.message.reply_text("Where are you right now?",
        reply_markup=build_location_keyboard("home","start")
    )

