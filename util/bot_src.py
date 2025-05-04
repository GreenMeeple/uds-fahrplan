from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations

# --- Static options ---
keyboard_flat = list(locations.keys())
inline_time_options = [0, 5, 10, 15, 30, 60]

def build_location_keyboard(session, step, exclude=None):
    buttons = [
        [InlineKeyboardButton(text=loc, callback_data=f"{session}:{step}:{loc}")]
        for loc in keyboard_flat if loc != exclude
    ]
    buttons += [[InlineKeyboardButton(text="More Stations", callback_data=f"{session}:more:more")]]
    return InlineKeyboardMarkup(buttons)

def build_time_keyboard(session):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{t} min" if t else "now", callback_data=f"{session}:time:{t}")]
        for t in inline_time_options
    ])

opt_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("trip", callback_data="trip:start:start")],
    [InlineKeyboardButton("depart", callback_data="depart:start:start")],
    [InlineKeyboardButton("home", callback_data="home:start:start")]
])

# --- Command handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Usage: /trip, /depart, /home — or click a button below:",
        reply_markup=opt_keyboard
    )

