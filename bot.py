from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
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
    usd, khr = extract_amounts(text)
    if usd or khr:
        data = load_data()
        data.append({
            "date": datetime.datetime.now().strftime('%Y-%m-%d'),
            "usd": usd,
            "khr": khr
        })
        save_data(data)

async def send_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.strip().lower()
    data = load_data()

    if cmd == '/today':
        target_date = datetime.datetime.now().strftime('%Y-%m-%d')
        label = "សរុបប្រតិបត្តិការ ថ្ងៃទី " + datetime.datetime.now().strftime('%d %b %Y')
    elif cmd == '/yesterday':
        target_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        label = "សរុបប្រតិបត្តិការ ម្សិលមិញ"
    elif cmd == '/total':
        target_date = None
        label = "សរុបប្រតិបត្តិការទាំងអស់"
    elif cmd.startswith('/day '):
        try:
            target_date = cmd.split()[1]
            datetime.datetime.strptime(target_date, '%Y-%m-%d')
            label = f"សរុបប្រតិបត្តិការ ថ្ងៃទី {target_date}"
        except:
            await update.message.reply_text("Please use date format: /day YYYY-MM-DD")
            return
    else:
        await update.message.reply_text("Commands supported:\n/today\n/yesterday\n/total\n/day YYYY-MM-DD")
        return

    total_usd = total_khr = count_usd = count_khr = 0

    for entry in data:
        if target_date is None or entry['date'] == target_date:
            if entry['usd'] > 0:
                total_usd += entry['usd']
                count_usd += 1
            if entry['khr'] > 0:
                total_khr += entry['khr']
                count_khr += 1

    reply = f"""{label}:

៛(KHR): {total_khr:,}   ចំនួនប្រតិបតិ្តការ​សរុប: {count_khr}
$(USD): {total_usd:.2f}   ចំនួនប្រតិបតិ្តការ​សរុប: {count_usd}"""
    await update.message.reply_text(reply)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = """📊 អ្នកអាចជ្រើសរើសមើលរបាយការណ៍:

• ប្រចាំថ្ងៃ (/today)
• ប្រចាំសប្ដាហ៍ (/week)
• ប្រចាំខែ (/month)
"""
    await update.message.reply_text(menu)

BOT_TOKEN = os.getenv('BOT_TOKEN')

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(CommandHandler(["today", "yesterday", "total", "day"], send_summary))
app.add_handler(CommandHandler("menu", show_menu))

app.run_polling()
