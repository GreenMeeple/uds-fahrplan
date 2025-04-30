import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from location import locations
from getTrips import parse_trips

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
async def trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    
    await update.message.reply_text(
        "🚌 Where do you want to start your journey?",
        reply_markup=build_location_keyboard()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Check what stage we're in
    if "start_location" not in context.user_data:
        if data not in locations:
            await query.edit_message_text("❗ Please choose a valid starting location.", reply_markup=build_location_keyboard())
            return
        context.user_data["start_location"] = data
        await query.edit_message_text(
            f"✅ Starting point set to {data}.\n\nChoose your departure time:",
            reply_markup=build_time_keyboard()
        )
    elif "time" not in context.user_data:
        if not data.isdigit() or int(data) not in inline_time_options:
            await query.edit_message_text("❗ Please choose a valid time option.", reply_markup=build_time_keyboard())
            return
        context.user_data["time"] = int(data)
        await query.edit_message_text(
            f"✅ Time set to {data} min later.\n\nNow, where do you want to go?",
            reply_markup=build_location_keyboard(exclude=context.user_data["start_location"])
        )
    else:
        if data not in locations:
            await query.edit_message_text("❗ Please choose a valid destination.", reply_markup=build_location_keyboard())
            return
        start = context.user_data["start_location"]
        time = context.user_data["time"]
        ziel = data

        await query.edit_message_text(f"🔍 Finding trips from {start} to {ziel} in {time} min...")

        trips_info = parse_trips(start, ziel, time)
        await query.edit_message_text(trips_info or "❌ Could not find trips. Please try again.")

        context.user_data.clear()

# --- Run bot ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    app.add_handler(CommandHandler("trip", trip))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🦉 Bot is running.")
    app.run_polling()
