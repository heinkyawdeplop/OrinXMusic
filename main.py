from pyrogram import Client

app = Client(
    "bot",
    api_id=31399150,
    api_hash="53d2e8122b1da92ede536640ed7f42de",
    bot_token="8164031458:AAGqi8GRQors7j79TbcmzX2Vz_jl2wJYb_w"
)

@app.on_message()
def hello(client, message):
    message.reply("Bot is working")

app.run()
