import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL
import os

API_ID = int(os.getenv("31399150"))
API_HASH = os.getenv("53d2e8122b1da92ede536640ed7f42de")
BOT_TOKEN = os.getenv("8164031458:AAGqi8GRQors7j79TbcmzX2Vz_jl2wJYb_w")
SESSION_STRING = os.getenv("BQHdt-kAIWorKiteblUTLMRdPqoI-yCMfv3HFnEcaaS210HHTd9DMNRMRtby63HTC5iPBnja3XJmlF737STkNrWJEtl2elPO7Dqw0OJlzrq4tkdE91G3xacaIosHSzYwt1eA_jMleFlRgluZzMhctaDgdu0q0QINgSjjxF18e7XZAnT7qFndBTsIvqbjIT9h8lnxlXa4ghIVTiqrA3nSxVvGLr3_m06H_yia_a2W2HY3bQD_K0spPqpCgYub_WNcNAghwqVqwWuihzl7yK9amh4wPDR3J93Muw-Tp9N4maSOiC1_9CQi_g0CYgGZYvfnxCyfR2mRk9dOWyQh3kRjiAPwtGS8agAAAAHrrYxIAA")

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

vc = PyTgCalls(assistant)

def get_audio(query):
    with YoutubeDL({"format": "bestaudio", "quiet": True}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return info["entries"][0]["url"], info["entries"][0]["title"]

@bot.on_message(filters.command("play"))
async def play(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Give song name")

    query = " ".join(msg.command[1:])
    stream, title = get_audio(query)

    await vc.join_group_call(
        msg.chat.id,
        AudioPiped(stream)
    )

    await msg.reply(f"▶️ Playing: {title}")

async def main():
    await bot.start()
    await assistant.start()
    await vc.start()
    print("VC Bot Running")
    await asyncio.Event().wait()

asyncio.run(main())
