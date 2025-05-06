from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getTrips import *
from util.getDepartures import *

# --- Static options ---
keyboard_flat = list(locations.keys())
inline_time_options = [0, 5, 10, 15, 30, 60]

def build_location_keyboard(session, step, exclude=None):
    buttons = [
        [InlineKeyboardButton(text=loc, callback_data=f"{session}:{step}:{loc}")]
        for loc in keyboard_flat if loc != exclude
    ]
    buttons += [[InlineKeyboardButton(text="More Stations", callback_data=f"{session}:more:{step}")]]
    if exclude is not None:
        buttons += [[InlineKeyboardButton(text="Back", callback_data=f"{session}:{step}:back")]]
    return InlineKeyboardMarkup(buttons)

def build_time_keyboard(session):
    buttons = [
        [InlineKeyboardButton(f"{t} min" if t else "now", callback_data=f"{session}:time:{t}")]
        for t in inline_time_options
    ]

    buttons += [[InlineKeyboardButton(text="Back", callback_data=f"{session}:time:back")]]
    return InlineKeyboardMarkup(buttons)

def build_session_keyboard(session):
    buttons = [
        [InlineKeyboardButton(text="Resume Previous Session", callback_data=f"{session}:session:resume")],
        [InlineKeyboardButton(text="Delete Previous Session and Continue", callback_data=f"{session}:session:continue")]
    ]
    return InlineKeyboardMarkup(buttons)

opt_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("trip", callback_data="trip:start:start")],
    [InlineKeyboardButton("depart", callback_data="depart:start:start")],
    [InlineKeyboardButton("home", callback_data="home:start:start")]
])

# --- Command handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data:
        context.user_data.clear()
        await update.message.reply_text("You are submiting a New request, previous session cleared."
    )
    await update.message.reply_text("""
/trip          Get connctions from A to B
/depart    Get departures of station A
/home      Get connections from A to your home"""
    )

