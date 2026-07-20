import asyncio
from telethon import events
import utils, database as db

def register(client):
    @client.on(events.NewMessage(pattern=r'^/broadcast(\s|$|@)'))
    async def broadcast_cmd(event):
        uid = event.sender_id
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(uid):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        msg = event.text.split(maxsplit=1)
        if len(msg) < 2:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /broadcast <message>")
            return
        text = msg[1]
        users = db.get_all_user_ids()
        sent = 0
        failed = 0
        status = await event.reply(f"𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁𝗶𝗻𝗴...\n━━━━━━━━━━━━━━━━━━━━\n╰ 𝟬/{len(users)}")
        for i, user_id in enumerate(users):
            try:
                m = await client.send_message(user_id, text, parse_mode='html')
                try:
                    await client.pin_message(user_id, m.id)
                except:
                    pass
                sent += 1
            except:
                failed += 1
            if (i + 1) % 5 == 0 or i == len(users) - 1:
                try:
                    await status.edit(f"𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁𝗶𝗻𝗴...\n━━━━━━━━━━━━━━━━━━━━\n╰ {i+1}/{len(users)}")
                except:
                    pass
        await status.edit(
            f"𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"╰ 𝗦𝗲𝗻𝘁: {sent}\n"
            f"╰ 𝗙𝗮𝗶𝗹𝗲𝗱: {failed}"
        )
