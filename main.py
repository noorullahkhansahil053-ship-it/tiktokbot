import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
    await update.message.reply_text("سلام! د TikTok لینک راولېږئ ترڅو ویډیو درته ښکته کړم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text.strip()

    if not await check_membership(user_id, context):
        await update.message.reply_text(f"مهرباني وکړئ لومړی زموږ په کانال {CHANNEL_USERNAME} کې غړي شئ، بیا لینک واستوئ.")
        return

    if "tiktok.com" not in url:
        await update.message.reply_text("مهرباني وکړئ سم د TikTok لینک واستوئ.")
        return

    msg = await update.message.reply_text("په پروسس کې دی، مهرباني وکړئ لږ صبر وکړئ...")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()

        if response.get("code") == 0:
            video_url = response["data"]["play"]
            video_bytes = requests.get(video_url).content

            with open("video.mp4", "wb") as f:
                f.write(video_bytes)

            with open("video.mp4", "rb") as video:
                await update.message.reply_video(video=video, caption="دا هم ستاسو ویډیو! ✅")

            await msg.delete()
            if os.path.exists("video.mp4"):
                os.remove("video.mp4")
        else:
            await msg.edit_text("خطا: د ویډیو موندل امکان نلري، لینک درست کړئ.")

    except Exception as e:
        await msg.edit_text(f"خطا په دانلود کې: {str(e)}")
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
