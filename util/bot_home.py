from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from util.profiles import locations
from util.getTrips import *
from util.getDepartures import *
from util.bot_src import *

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["home_session"] = {}
    await update.message.reply_text("Where are you right now?",
        reply_markup=build_location_keyboard("home","start")
    )

