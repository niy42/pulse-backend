import asyncio
from turtle import update

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from app.services.process_video import process_video
from app.config import TELEGRAM_BOT_TOKEN

# 🧠 In-memory usage tracking (MVP only)
user_usage = {}
FREE_LIMIT = 3  # 3 free content pack per user


def split_text(text: str, size: int = 3500):
    return [text[i : i + size] for i in range(0, len(text), size)]


# 🚀 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send me a YouTube link 🎥\n\n"
        "I’ll turn it into:\n"
        "🔥 Viral hooks\n"
        "🧠 Insight posts\n"
        "💥 Contrarian takes\n"
        "📌 Summary\n\n"
        "Ready to post instantly."
    )


# 💸 UPGRADE MESSAGE
async def send_upgrade_message(update: Update):
    if not update.message:
        return

    keyboard = [
        [InlineKeyboardButton("🚀 Upgrade Now", url="https://t.me/yourusername")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚡ You've used your free content pack.\n\n"
        "Creators using this tool are posting 5–10x more consistently and growing faster.\n\n"
        "Upgrade to unlock:\n"
        "✅ Unlimited content packs\n"
        "✅ Better viral hooks\n"
        "✅ Faster generation\n\n"
        "Don’t lose momentum.",
        reply_markup=reply_markup,
    )


from telegram.ext import ContextTypes


async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔥 ANY MESSAGE RECEIVED")


# 🧠 MAIN MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text
    user = update.message.from_user

    if not user:
        return

    user_id = user.id

    # Initialize user usage
    if user_id not in user_usage:
        user_usage[user_id] = 0

    # Check usage limit BEFORE processing
    if user_usage[user_id] >= FREE_LIMIT:
        await send_upgrade_message(update)
        return

    # Validate YouTube link
    if not text or ("youtube.com" not in text and "youtu.be" not in text):
        await update.message.reply_text(
            "❌ Send a valid YouTube link.\n\nExample:\nhttps://youtube.com/..."
        )
        return

    await update.message.reply_text("⚙️ Processing your video...")

    try:
        status = await update.message.reply_text("⏳ Extracting transcript...")

        result = await process_video(text)

        if not result:
            await status.edit_text(
                "❌ Couldn't extract content from this video.\nTry another link."
            )
            return

        # 🧠 HOOKS
        await status.edit_text("🔥 Generating hooks...")
        await asyncio.sleep(0.8)

        for chunk in split_text("\n".join(result.hooks)):
            await update.message.reply_text(f"🔥 HOOKS\n\n{chunk}")

        # 💡 INSIGHTS
        await status.edit_text("🧠 Building insights...")
        await asyncio.sleep(0.8)

        for chunk in split_text("\n".join(result.insights)):
            await update.message.reply_text(f"🧠 INSIGHTS\n\n{chunk}")

        # 💥 CONTRARIAN
        await status.edit_text("⚔️ Crafting contrarian takes...")
        await asyncio.sleep(0.8)

        for chunk in split_text("\n".join(result.contrarian)):
            await update.message.reply_text(f"💥 CONTRARIAN\n\n{chunk}")

        # 📌 SUMMARY
        await status.edit_text("📌 Finalizing summary...")
        await asyncio.sleep(0.8)

        for chunk in split_text("\n".join(result.summary)):
            await update.message.reply_text(f"📌 SUMMARY\n\n{chunk}")

        # 💬 QUOTES
        await status.edit_text("💬 Extracting quotes...")
        await asyncio.sleep(0.8)

        for chunk in split_text("\n".join(result.quotes)):
            await update.message.reply_text(f"💬 QUOTES\n\n{chunk}")

        # ✅ DONE
        await status.edit_text("✅ Content pack ready!")

        user_usage[user_id] += 1

        if user_usage[user_id] == 1:
            await update.message.reply_text(
                "🔥 This was your free content pack.\n\n"
                "Next time, you’ll need to upgrade to keep generating."
            )

        keyboard = [
            [InlineKeyboardButton("🔥 Generate Again", callback_data="retry")],
            [InlineKeyboardButton("💡 Tips", callback_data="tips")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=reply_markup,
        )

    except Exception as e:
        print(e)
        await update.message.reply_text("⚠️ Something went wrong. Try again.")


# 🔘 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    if not query.message:
        return

    if query.data == "retry":
        await query.message.reply_text(  # type: ignore
            "🎥 Send another YouTube link and I’ll generate a new content pack."
        )

    elif query.data == "tips":
        await query.message.reply_text(  # type: ignore
            "💡 Tips to get better results:\n\n"
            "- Use videos with strong opinions\n"
            "- Avoid low-quality audio\n"
            "- Shorter videos = sharper content\n"
            "- Post consistently for growth 🚀"
        )


import asyncio


# def run_bot():
#     application = Application.builder().token(TELEGRAM_BOT_TOKEN or "").build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(
#         MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
#     )
#     application.add_handler(CallbackQueryHandler(button_handler))
#     application.add_handler(MessageHandler(filters.ALL, debug_handler))

#     print("Bot running...")

#     async def start_bot():
#         await application.initialize()
#         await application.start()
#         await application.updater.start_polling()

#     asyncio.run(start_bot())


# 🚀 BOT RUNNER
def run_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN or "").build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
