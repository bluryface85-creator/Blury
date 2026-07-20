import random, string, time
import utils, database as db
from telethon import Button, events
from utils import sbold

def register(client):
    @client.on(events.NewMessage(pattern=r'^/gkey(\s|$|@)'))
    async def gen_key(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            parts = event.text.split()
            plan = parts[1].upper()
            amount = int(parts[2]) if len(parts) > 2 else 1
            if plan not in ("LITE", "BASIC", "X", "RIP") or amount < 1:
                raise Exception()
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /gkey <plan> [amount]\n𝗣𝗹𝗮𝗻𝘀: lite, basic, x, rip")
            return

        keys = []
        for _ in range(amount):
            while True:
                k = f"{plan}-" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                if db.add_key(k, plan):
                    keys.append(k)
                    break

        keys_text = "\n".join(f"┗ <code>{k}</code>" for k in keys)
        msg = (
            f"𝗞𝗲𝘆𝘀 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"┣ 𝗣𝗹𝗮𝗻 ➜ <code>{sbold(plan)}</code>\n"
            f"┣ 𝗖𝗼𝘂𝗻𝘁 ➜ <code>{amount}</code>\n"
            f"┣ 𝗞𝗲𝘆𝘀 💎\n"
            f"{keys_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"𝗨𝘀𝗲𝗿𝘀 𝗿𝗲𝗱𝗲𝗲𝗺 𝘄𝗶𝘁𝗵 /redeem [key]"
        )
        await event.reply(utils.premium_emoji(msg), parse_mode='html')
