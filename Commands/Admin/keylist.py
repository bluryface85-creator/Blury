import time
import utils, database as db
from utils import sbold
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^/keylist(\s|$|@)'))
    async def key_list(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        keys = db.get_unredeemed_keys()
        if not keys:
            await event.reply("𝗡𝗼 𝘂𝗻𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱 𝗸𝗲𝘆𝘀")
            return
        lines = []
        for k in keys:
            ts = time.strftime("%Y-%m-%d", time.localtime(k["created_at"]))
            lines.append(f"┣ <code>{k['key']}</code> ━ [{sbold(k['plan'].upper())}] ━ {ts}")
        text = (
            f"𝗨𝗻𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱 𝗞𝗲𝘆𝘀\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{chr(10).join(lines)}"
        )
        await event.reply(text, parse_mode='html')
