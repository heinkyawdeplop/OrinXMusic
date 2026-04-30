import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

API_ID = 31307753
API_HASH = "5edb328f3e02579528f835dd4652d3b0"
BOT_TOKEN = "8689579971:AAHweO5izJvd9rACCMBv52LrB1P-nprs-yc"

# Assistant Account
SESSION_STRING = "BQHdt-kAIWorKiteblUTLMRdPqoI-yCMfv3HFnEcaaS210HHTd9DMNRMRtby63HTC5iPBnja3XJmlF737STkNrWJEtl2elPO7Dqw0OJlzrq4tkdE91G3xacaIosHSzYwt1eA_jMleFlRgluZzMhctaDgdu0q0QINgSjjxF18e7XZAnT7qFndBTsIvqbjIT9h8lnxlXa4ghIVTiqrA3nSxVvGLr3_m06H_yia_a2W2HY3bQD_K0spPqpCgYub_WNcNAghwqVqwWuihzl7yK9amh4wPDR3J93Muw-Tp9N4maSOiC1_9CQi_g0CYgGZYvfnxCyfR2mRk9dOWyQh3kRjiAPwtGS8agAAAAHrrYxIAA"

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

call = PyTgCalls(assistant)

# Queue storage
QUEUE = {}

# ---------- YT SEARCH ----------
def yt_search(query):
    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["webpage_url"], info["title"], info["duration"]

# ---------- STREAM ----------
def get_stream(url):
    with YoutubeDL({"format": "bestaudio", "quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"]

# ---------- FORMAT TIME ----------
def format_time(seconds):
    if not seconds:
        return "Live"
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

# ---------- PLAY NEXT ----------
async def play_next(chat_id):
    if chat_id not in QUEUE or len(QUEUE[chat_id]) == 0:
        await call.leave_group_call(chat_id)
        return

    song = QUEUE[chat_id].pop(0)
    stream = get_stream(song["url"])

    await call.change_stream(chat_id, AudioPiped(stream))

# ---------- START ----------
@bot.on_message(filters.command("start"))
async def start(_, m):
    await m.reply("🎧 Advanced Music Bot Ready!\nUse /play <name or link>")

# ---------- PLAY ----------
@bot.on_message(filters.command("play"))
async def play(_, m):
    if len(m.command) < 2:
        return await m.reply("❌ Give song name or link")

    query = " ".join(m.command[1:])
    await m.reply("🔎 Searching...")

    try:
        if "youtube.com" in query or "youtu.be" in query:
            url = query
            title = "Unknown"
            duration = 0
        else:
            url, title, duration = yt_search(query)

        song = {
            "url": url,
            "title": title,
            "duration": duration
        }

        chat_id = m.chat.id

        if chat_id not in QUEUE:
            QUEUE[chat_id] = []

        QUEUE[chat_id].append(song)

        # If first song → play immediately
        if len(QUEUE[chat_id]) == 1:
            stream = get_stream(url)

            await call.join_group_call(
                chat_id,
                AudioPiped(stream)
            )

            await m.reply(f"▶️ Playing:\n{title}\n⏱ {format_time(duration)}")
        else:
            await m.reply(f"➕ Added to queue:\n{title}\n⏱ {format_time(duration)}")

    except Exception as e:
        await m.reply(f"❌ Error:\n{e}")

# ---------- SKIP ----------
@bot.on_message(filters.command("skip"))
async def skip(_, m):
    chat_id = m.chat.id
    await play_next(chat_id)
    await m.reply("⏭ Skipped")

# ---------- PAUSE ----------
@bot.on_message(filters.command("pause"))
async def pause(_, m):
    await call.pause_stream(m.chat.id)
    await m.reply("⏸ Paused")

# ---------- RESUME ----------
@bot.on_message(filters.command("resume"))
async def resume(_, m):
    await call.resume_stream(m.chat.id)
    await m.reply("▶️ Resumed")

# ---------- STOP ----------
@bot.on_message(filters.command("stop"))
async def stop(_, m):
    chat_id = m.chat.id
    QUEUE[chat_id] = []
    await call.leave_group_call(chat_id)
    await m.reply("⏹ Stopped & Cleared Queue")

# ---------- QUEUE ----------
@bot.on_message(filters.command("queue"))
async def queue(_, m):
    chat_id = m.chat.id

    if chat_id not in QUEUE or not QUEUE[chat_id]:
        return await m.reply("📭 Queue empty")

    text = "🎶 Queue:\n\n"
    for i, song in enumerate(QUEUE[chat_id], start=1):
        text += f"{i}. {song['title']} ({format_time(song['duration'])})\n"

    await m.reply(text)

# ---------- AUTO PLAY NEXT ----------
@call.on_stream_end()
async def stream_end_handler(_, update):
    await play_next(update.chat_id)

# ---------- RUN ----------
async def main():
    await bot.start()
    await assistant.start()
    await call.start()
    print("🔥 Music Bot Running...")

    await asyncio.Event().wait()

asyncio.run(main())