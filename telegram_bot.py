import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from util.profiles import locations
from util.getTrips import *

load_dotenv()

# --- Static keyboard options ---
keyboard_flat = list(locations.keys())
inline_time_options = [0, 5, 10, 15, 30, 60]

def build_location_keyboard(exclude=None):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=loc, callback_data=loc)]
        for loc in keyboard_flat if loc != exclude
    ])

def build_time_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{t} min" if t else "now", callback_data=str(t))]
        for t in inline_time_options
    ])

# --- Handlers ---
async def trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    
    await update.message.reply_text(
        "🚌 Where do you want to start your journey?",
        reply_markup=build_location_keyboard()
    )

async def handle_start_location(query, context, data):
    if data not in locations:
        await query.edit_message_text("❗ Please choose a valid starting location.", reply_markup=build_location_keyboard())
        return
    context.user_data["start_location"] = data
    await query.edit_message_text(
        f"✅ Starting point set to {data}.\n\nChoose your departure time:",
        reply_markup=build_time_keyboard()
    )

async def handle_time_selection(query, context, data):
    if not data.isdigit() or int(data) not in inline_time_options:
        await query.edit_message_text("❗ Please choose a valid time option.", reply_markup=build_time_keyboard())
        return
    context.user_data["time"] = int(data)
    await query.edit_message_text(
        f"✅ Time set to {data} min later.\n\nNow, where do you want to go?",
        reply_markup=build_location_keyboard(exclude=context.user_data["start_location"])
    )

async def handle_destination(query, context, data):
    if data not in locations:
        await query.edit_message_text("❗ Please choose a valid destination.", reply_markup=build_location_keyboard())
        return
    
    context.user_data["destination"] = data
    await query.edit_message_text(f"🔍 Finding trips from {context.user_data["start_location"]} to {data} in {context.user_data["time"]} min...")

    context.user_data["trip"] = get_trips("saarvv", context.user_data["start_location"], data, context.user_data["time"],)
    btn_details = InlineKeyboardMarkup([[InlineKeyboardButton("details", callback_data="details")]])
    btn_again = InlineKeyboardMarkup([[InlineKeyboardButton("again", callback_data="again")]])

    if context.user_data["trip"]:
        trip_basic = parse_trips_basic(context.user_data["trip"])
        await query.edit_message_text(text=trip_basic, reply_markup=btn_details)
    else:
        await query.edit_message_text(text="❌ Could not find trips. Please try again.", reply_markup=btn_again)

async def handle_finish(query, context, data):
    if data == "again":
        context.user_data.clear()
        await query.edit_message_text(
            "🚌 Where do you want to start your journey?",
            reply_markup=build_location_keyboard()
        )
    else:
        trips_details = parse_trips_detail(context.user_data["trip"])
        await query.edit_message_text(text=trips_details)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if "start_location" not in context.user_data:
        await handle_start_location(query, context, data)
    elif "time" not in context.user_data:
        await handle_time_selection(query, context, data)
    elif "destination" not in context.user_data:
        await handle_destination(query, context, data)
    else:
        await handle_finish(query, context, data)

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    
    await update.message.reply_text(
        "🚌 Where do you want to start your journey?",
        reply_markup=build_location_keyboard()
    )

# --- Run bot ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    app.add_handler(CommandHandler("trip", trips))
    app.add_handler(CommandHandler("home", home))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🦉 Bot is running.")
    app.run_polling()
