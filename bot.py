from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler,
    CommandHandler, filters
)
import datetime
import json
import os
import re

DATA_FILE = 'income.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def extract_amounts(text):
    khr_match = re.search(r"ចំនួន\s*([\d,]+)\s*រៀល", text)
    usd_match = re.search(r"\$([\d\.]+)", text)

    khr = int(khr_match.group(1).replace(',', '')) if khr_match else 0
    usd = float(usd_match.group(1)) if usd_match else 0
    return usd, khr

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Handle button text
    if text.startswith("Jul"):
        date = "2025-" + datetime.datetime.strptime(text, "%b %d").strftime("%m-%d")
        await send_summary_by_date(update, date)
        return

    if text == "⬅ ត្រឡប់ក្រោយ":
        await show_menu(update, context)
        return

    if text == "ប្រចាំថ្ងៃ":
        await show_day_buttons(update)
        return

    if text == "ប្រចាំសប្ដាហ៍":
        await update.message.reply_text("📅 Coming soon: សរុបប្រចាំសប្ដាហ៍")
        return

    if text == "ប្រចាំខែ":
        await update.message.reply_text("📅 Coming soon: សរុបប្រចាំខែ")
        return

    # Save payments
    usd, khr = extract_amounts(text)
    if usd or khr:
        data = load_data()
        data.append({
            "date": datetime.datetime.now().strftime('%Y-%m-%d'),
            "usd": usd,
            "khr": khr
        })
        save_data(data)

async def send_summary_by_date(update, target_date):
    data = load_data()

    total_usd = total_khr = count_usd = count_khr = 0
    for entry in data:
        if entry['date'] == target_date:
            if entry['usd'] > 0:
                total_usd += entry['usd']
                count_usd += 1
            if entry['khr'] > 0:
                total_khr += entry['khr']
                count_khr += 1

    label = f"📅 សរុបប្រតិបត្តិការ ថ្ងៃទី {target_date}"
    reply = f"""{label}:

៛(KHR): {total_khr:,}   ចំនួនប្រតិបតិ្តការ: {count_khr}
$(USD): {total_usd:.2f}   ចំនួនប្រតិបតិ្តការ: {count_usd}"""

    await update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())

async def show_day_buttons(update: Update):
    today = datetime.date.today()
    keyboard = [
        [KeyboardButton((today - datetime.timedelta(days=i)).strftime('%b %d')) for i in range(0, 3)],
        [KeyboardButton("ថ្ងៃផ្សេងទៀត"), KeyboardButton("⬅ ត្រឡប់ក្រោយ")]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("📅 សូមជ្រើសរើសថ្ងៃ៖", reply_markup=markup)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("ប្រចាំថ្ងៃ")],
        [KeyboardButton("ប្រចាំសប្ដាហ៍")],
        [KeyboardButton("ប្រចាំខែ")]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("📊 សូមជ្រើសរើសរបាយការណ៍៖", reply_markup=markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_menu(update, context)

BOT_TOKEN = os.getenv('BOT_TOKEN')

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("menu", show_menu))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

app.run_polling()

