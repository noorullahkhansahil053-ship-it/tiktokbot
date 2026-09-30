import os, re, asyncio, logging, mimetypes, requests
from urllib.parse import urlparse, unquote
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.WARNING)

TOKEN = os.environ.get("BOT_TOKEN") or open("token.txt").read().strip()
CHANNEL_USERNAME = "@NoorChannel167yi"

MAX_MB = 50
VIDEO = (".mp4", ".mov", ".mkv", ".webm", ".m4v")
IMAGE = (".jpg", ".jpeg", ".png", ".webp", ".gif")
FILES = (".pdf", ".mp3", ".zip", ".apk", ".m4a")

async def check_sub(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return False

def ytdl(url):
    opts = {"outtmpl": "dl_%(id)s.%(ext)s", "quiet": True, "noplaylist": True}
    if os.path.exists("cookies.txt"):
        opts["cookiefile"] = "cookies.txt"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_sub(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 په کانال کې جوین شئ", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        await update.message.reply_text(
            "⚠️ **سلامونه!**\nد ربات د کارولو لپاره لومړی زموږ په کانال کې غړیتوب واخلئ، بیا لینک راولېږئ.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    await update.message.reply_text("سلام! د ټیک ټاک لینک راولېږه ترڅو درته ډانلوډ یې کړم.")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_sub(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 په کانال کې جوین شئ", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        await update.message.reply_text(
            "⚠️ **سلامونه!**\nد ربات د کارولو لپاره لومړی زموږ په کانال کې غړیتوب واخلئ، بیا لینک راولېږئ.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    
    url = update.message.text
    msg = await update.message.reply_text("د ویډیو د ډانلوډولو پروسس روان دی... ⏳")
    try:
        file_path = await asyncio.to_thread(ytdl, url)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                if file_path.endswith(VIDEO):
                    await update.message.reply_video(video=f)
                else:
                    await update.message.reply_document(document=f)
            os.remove(file_path)
            await msg.delete()
        else:
            await msg.edit_text("❌ د فایل په ډاونلوډ کې ستونزه راغله.")
    except Exception as e:
        await msg.edit_text(f"❌ خطا: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.run_polling()

if __name__ == "__main__":
    main()
