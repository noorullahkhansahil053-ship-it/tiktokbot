import os, re, asyncio, logging, mimetypes, requests
from urllib.parse import urlparse, unquote
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.WARNING)
TOKEN = open("token.txt").read().strip()
MAX_MB = 50
VIDEO = (".mp4", ".mov", ".mkv", ".webm", ".m4v")
IMAGE = (".jpg", ".jpeg", ".png", ".webp", ".gif")
FILES = (".pdf", ".mp3", ".zip", ".apk", ".m4a")

def ytdl(url):
    opts = {"outtmpl": "dl_%(id)s.%(ext)s", "format": "mp4/best",
            "quiet": True, "noplaylist": True}
    if os.path.exists("cookies.txt"):
        opts["cookiefile"] = "cookies.txt"
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info(url, download=True)
        return y.prepare_filename(info)

def direct(url):
    r = requests.get(url, stream=True, timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    ct = r.headers.get("content-type", "").split(";")[0]
    if ct == "text/html":
        raise ValueError("html page")
    name = os.path.basename(unquote(urlparse(url).path)) or "file"
    name = "dl_" + re.sub(r"[^\w.\-]", "_", name)[-60:]
    if not os.path.splitext(name)[1]:
        name += mimetypes.guess_extension(ct) or ""
    size = 0
    try:
        with open(name, "wb") as f:
            for c in r.iter_content(65536):
                size += len(c)
                if size > MAX_MB * 1024 * 1024:
                    raise ValueError("too big")
                f.write(c)
    except Exception:
        if os.path.exists(name):
            os.remove(name)
        raise
    return name

def get(url):
    clean = url.lower().split("?")[0]
    if clean.endswith(VIDEO + IMAGE + FILES):
        return direct(url)
    try:
        return ytdl(url)
    except Exception:
        return direct(url)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! د TikTok، Instagram، Facebook، YouTube یا هر ویډیو/عکس لینک راولیږئ.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = re.search(r"https?://\S+", update.message.text or "")
    if not m:
        await update.message.reply_text("مهرباني وکړئ لینک راولیږئ.")
        return
    msg = await update.message.reply_text("ډاونلوډ کیږي...")
    path = None
    try:
        path = await asyncio.to_thread(get, m.group(0))
        size = os.path.getsize(path)
        if size > MAX_MB * 1024 * 1024:
            await msg.edit_text("فایل ډېر لوی دی (له 50MB زیات).")
            return
        ext = os.path.splitext(path)[1].lower()
        with open(path, "rb") as f:
            if ext in VIDEO:
                await update.message.reply_video(f)
            elif ext in IMAGE and size < 10 * 1024 * 1024:
                await update.message.reply_photo(f)
            else:
                await update.message.reply_document(f)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("ډاونلوډ ونه شو. لینک وګورئ (خصوصي پوسټونه نه کیږي).")
        print("Error:", e)
    finally:
        if path and os.path.exists(path):
            os.remove(path)

def main():
    app = (Application.builder().token(TOKEN)
           .connect_timeout(30).read_timeout(60).write_timeout(60).build())
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Downloader bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
