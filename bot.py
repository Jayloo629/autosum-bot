import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Sample data: replace this with your real data source
data = [
    {'date': '2025-07-10', 'currency': 'USD', 'amount': 100},
    {'date': '2025-07-10', 'currency': 'KHR', 'amount': 400000},
    {'date': '2025-07-09', 'currency': 'USD', 'amount': 50},
    {'date': '2025-07-09', 'currency': 'KHR', 'amount': 200000},
    # Add more entries as needed
]

async def send_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.strip().lower()

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
            # Validate date format
            datetime.datetime.strptime(target_date, '%Y-%m-%d')
            label = f"សរុបប្រតិបត្តិការ ថ្ងៃទី {target_date}"
        except Exception:
            await update.message.reply_text("សូមប្រើទ្រង់ទ្រាយកាលបរិច្ឆេទ៖ /day YYYY-MM-DD")
            return
    else:
        await update.message.reply_text(
            "Commands supported:\n"
            "/today - ប្រចាំថ្ងៃ\n"
            "/yesterday - ប្រចាំម្សិលមិញ\n"
            "/total - សរុបប្រតិបត្តិការទាំងអស់\n"
            "/day YYYY-MM-DD - របាយការណ៍ប្រចាំថ្ងៃជាក់លាក់"
        )
        return

    # Summarize payments
    total_usd = 0
    total_khr = 0
    count_usd = 0
    count_khr = 0

    for entry in data:
        if target_date is None or entry['date'] == target_date:
            if entry['currency'] == 'USD':
                total_usd += entry['amount']
                count_usd += 1
            elif entry['currency'] == 'KHR':
                total_khr += entry['amount']
                count_khr += 1

    reply = (
        f"{label}\n"
        f"៛ (KHR): {total_khr:,}   ចំនួនប្រតិបតិ្តការ​សរុប: {count_khr}\n"
        f"$ (USD): {total_usd:.2f}   ចំនួនប្រតិបតិ្តការ​សរុប: {count_usd}"
    )
    await update.message.reply_text(reply)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សូមអភ័យទោស, មិនទាន់គាំទ្រកម្មង់នេះទេ។ សូមប្រើ /today, /yesterday, /total ឬ /day YYYY-MM-DD។")

def main():
    # Replace with your bot token
    TOKEN = "YOUR_BOT_TOKEN"

    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers for commands
    app.add_handler(CommandHandler(["today", "yesterday", "total", "day"], send_summary))

    # Catch all other commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
