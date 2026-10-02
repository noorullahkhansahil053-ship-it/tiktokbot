import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@NoorChannel167yi"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! د ټیک‌تاک لینک راولېږئ ترڅو ویډیو درته ښکته کړم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text.strip()

    if not await check_membership(user_id, context):
        await update.message.reply_text(f"مهرباني وکړئ لومړی زموږ په کانال {CHANNEL_USERNAME} کې غړی شئ، بیا لینک واستوئ.")
        return

    if "tiktok.com" not in url:
        await update.message.reply_text("مهرباني وکړئ درست د TikTok لینک واستوئ.")
        return

    msg = await update.message.reply_text("په پروسس کې دی، مهرباني وکړئ لږ صبر وکړئ...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'tiktok': {
                'webpage_download': True,
            }
        }
    }

    try:
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open('video.mp4', 'rb') as video:
            await update.message.reply_video(video=video, caption="دا هم ستاسو ویډیو! ✅")
        
        await msg.delete()
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')

    except Exception as e:
        await msg.edit_text(f"خطا په دانلود کې: {str(e)}")
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
