from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getTrips import *
from util.getDepartures import *

# --- Static keyboard options ---
keyboard_flat = list(locations.keys())
inline_time_options = [0, 5, 10, 15, 30, 60]
time_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton(f"{t} min" if t else "now", callback_data=str(t))]
    for t in inline_time_options
])
opt_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("trip", callback_data="trip")],
    [InlineKeyboardButton("depart", callback_data="depart")],
    [InlineKeyboardButton("home", callback_data="home")],
])

def build_location_keyboard(exclude=None):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=loc, callback_data=loc)]
        for loc in keyboard_flat if loc != exclude
    ])

# --- Handlers ---
async def handle_trip_start(query, context, data):
    if data not in locations:
        await query.edit_message_text("❗ Please choose a valid starting location.", reply_markup=build_location_keyboard())
        return
    context.user_data["start"] = data
    await query.edit_message_text(
        f"✅ Starting point set to {data}.\n\nChoose your departure time:",
        reply_markup=time_keyboard
    )

async def handle_trip_time(query, context, data):
    if not data.isdigit() or int(data) not in inline_time_options:
        await query.edit_message_text("❗ Please choose a valid time option.", reply_markup=time_keyboard)
        return
    context.user_data["time"] = int(data)
    await query.edit_message_text(
        f"✅ Time set to {data} min later.\n\nNow, where do you want to go?",
        reply_markup=build_location_keyboard(exclude=context.user_data["start"])
    )

async def handle_trip_destination(query, context, data):
    if data not in locations:
        await query.edit_message_text("❗ Please choose a valid destination.", reply_markup=build_location_keyboard())
        return
    await query.edit_message_text(f"🔍 Finding trips from {context.user_data["start"]} to {data} ...")

    context.user_data["destination"] = data
    context.user_data["trip"] = get_trips("saarvv", context.user_data["start"], data, context.user_data["time"],)

    if context.user_data["trip"]:
        btn_details = InlineKeyboardMarkup([[InlineKeyboardButton("details", callback_data="details")]])
        await query.edit_message_text(text=parse_trips_basic(context.user_data["trip"]), reply_markup=btn_details)
    else:
        btn_again = InlineKeyboardMarkup([[InlineKeyboardButton("again", callback_data="again")]])
        await query.edit_message_text(text="❌ Could not find trips. Please try again.", reply_markup=btn_again)

async def handle_trip_details(query, context, data):
    if data == "again":
        context.user_data.clear()
        await query.edit_message_text(
            "🚌 Where do you want to start your journey?",
            reply_markup=build_location_keyboard()
        )
    else:
        trips_details = parse_trips_detail(context.user_data["trip"])
        await query.edit_message_text(text=trips_details)

async def handle_depart_start(query, context, data):
    if data not in locations:
        await query.edit_message_text("❗ Please choose a valid starting location.", reply_markup=build_location_keyboard())
        return
    context.user_data["start"] = data
    await query.edit_message_text(
        f"✅ Station are set to {data}.\n\nChoose the departure time:",
        reply_markup=time_keyboard
    )

async def handle_depart_time(query, context, data):
    if not data.isdigit() or int(data) not in inline_time_options:
        await query.edit_message_text("❗ Please choose a valid time option.", reply_markup=time_keyboard)
        return
    
    await query.edit_message_text(f"🔍 Finding departures from {context.user_data["start"]} ...")
    departures = get_departures("saarvv", context.user_data["start"], int(data))

    await query.edit_message_text(parse_departures(departures))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    try:
        if context.user_data["begin"]:
            context.user_data["opt"] = data
            context.user_data["begin"] = None
    except Exception as e:
            print(f"⚠️ Error parsing journey: {e}")

    match context.user_data["opt"]:
        case "trip": 
            if "start" not in context.user_data:
                await handle_trip_start(query, context, data)
            elif "time" not in context.user_data:
                await handle_trip_time(query, context, data)
            elif "destination" not in context.user_data:
                await handle_trip_destination(query, context, data)
            else:
                await handle_trip_details(query, context, data)

        case "home":
            await query.edit_message_text("🚌 Testing Done")
        case "depart":
            if "start" not in context.user_data:
                await handle_depart_start(query, context, data)
            else:
                await handle_depart_time(query, context, data)

async def trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["opt"] = "trip"
    await update.message.reply_text(
        "🚌 Where do you want to start your journey?",
        reply_markup=build_location_keyboard()
    )

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["opt"] = "home"
    await update.message.reply_text("Where are you right now?",
        reply_markup=build_location_keyboard()
    )

async def depart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["opt"] = "depart"
    await update.message.reply_text("Which station do you want to know?",
        reply_markup=build_location_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["begin"] = True
    await update.message.reply_text(
        "Usage: /trip, /depart, /home, or click button below",
        reply_markup=opt_keyboard
    )
