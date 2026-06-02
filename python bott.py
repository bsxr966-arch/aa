import nest_asyncio
nest_asyncio.apply()

import os, re, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

TOKEN = "8067899125:AAHEavlIodQZwF0sHVtjlngif8SP953JJaY"

os.makedirs("downloads", exist_ok=True)

PATTERNS = {
    "tiktok": r"(tiktok\.com|vm\.tiktok\.com)",
    "instagram": r"(instagram\.com|instagr\.am)",
    "twitter": r"(twitter\.com|x\.com)",
}

def plat(url):
    for n, p in PATTERNS.items():
        if re.search(p, url, re.I):
            return n
    return None

async def dl(url):
    def _d():
        with yt_dlp.YoutubeDL({"format": "best[ext=mp4]/best", "outtmpl": "downloads/%(id)s.%(ext)s", "quiet": True}) as y:
            i = y.extract_info(url, download=True)
            return f"downloads/{i['id']}.mp4"
    return await asyncio.to_thread(_d)

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    name = u.effective_user.first_name or u.effective_user.username or "User"
    keyboard = [[
        InlineKeyboardButton("X", callback_data="X"),
        InlineKeyboardButton("Instagram", callback_data="instagram"),
        InlineKeyboardButton("TikTok", callback_data="tiktok"),
    ]]
    reply = InlineKeyboardMarkup(keyboard)
    await u.message.reply_text(
        f"Hello: {name}\nWelcome to Rafif bot",
        reply_markup=reply
    )

async def button(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    await q.edit_message_text(f"Send a {q.data} link")

async def h(u: Update, c: ContextTypes.DEFAULT_TYPE):
    url = u.message.text.strip()
    if not re.search(r"https?://", url):
        await u.message.reply_text("bad url")
        return
    p = plat(url)
    if not p:
        await u.message.reply_text("unsupported")
        return
    m = await u.message.reply_text("dl...")
    try:
        path = await dl(url)
        with open(path, "rb") as f:
            await u.message.reply_video(f)
        os.remove(path)
        await m.delete()
    except Exception as e:
        await m.edit_text(f"err: {str(e)[:200]}")

async def main():
    a = Application.builder().token(TOKEN).build()
    a.add_handler(CommandHandler("start", start))
    a.add_handler(CallbackQueryHandler(button))
    a.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h))
    await a.initialize()
    await a.start()
    await a.updater.start_polling()
    print("running")
    await asyncio.Event().wait()

asyncio.run(main())