from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import base64, zlib, marshal, os, asyncio, logging, traceback

logging.basicConfig(level=logging.INFO)

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

REQUIRED_CHANNEL = "@RawoARCHiv"

async def is_user_member(client, user_id):
    async for user in client.iter_participants(REQUIRED_CHANNEL):
        if user.id == user_id:
            return True
    return False

async def check_membership(event):
    sender = await event.get_sender()
    if await is_user_member(event.client, sender.id):
        return True
    await event.reply(
        "❌ Botu kullanmak için kanala katıl:\n"
        "https://t.me/RawoARCHiv"
    )
    return False

async def main():
    client = TelegramClient("encoder_bot", api_id, api_hash)

    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        if not await check_membership(event): return
        await event.reply(
            "Selam 👋 .py dosyanı gönder, encode edeyim 🚀"
        )

    @client.on(events.NewMessage(func=lambda e: e.file and e.file.ext == ".py"))
    async def encode_py(event):
        if not await check_membership(event): return
        try:
            path = await event.download_media()
            code = open(path, "r", encoding="utf-8").read()

            compiled = compile(code, "<string>", "exec")
            payload = base64.b64encode(zlib.compress(marshal.dumps(compiled))).decode()

            loader = f"""
import base64,zlib,marshal
exec(marshal.loads(zlib.decompress(base64.b64decode("{payload}"))))
"""
            out = path.replace(".py", "_encoded.py")
            open(out, "w", encoding="utf-8").write(loader)

            await event.reply("✅ Encode tamam", file=out)
            os.remove(path); os.remove(out)

        except Exception:
            await event.reply("❌ Hata oluştu")

    await client.start(bot_token=bot_token)
    await client.run_until_disconnected()

asyncio.run(main())
