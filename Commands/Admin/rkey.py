import time
import utils, database as db
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^/rkey(\s|$|@)'))
    async def revoke_key(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            target = event.text.split()[1].strip()
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /rkey <key> or /rkey all")
            return

        if target == "all":
            db.revoke_all_keys()
            await event.reply(
                "❌ 𝗞𝗲𝘆𝘀 𝗥𝗲𝘃𝗼𝗸𝗲𝗱\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 𝗔𝗹𝗹 𝘂𝗻𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱 𝗸𝗲𝘆𝘀 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗿𝗲𝘃𝗼𝗸𝗲𝗱\n"
                f"┗ 𝗧𝗵𝗲𝘀𝗲 𝗸𝗲𝘆𝘀 𝘄𝗶𝗹𝗹 𝗻𝗼 𝗹𝗼𝗻𝗴𝗲𝗿 𝘄𝗼𝗿𝗸"
            )
            return

        row = db.get_key(target)
        if not row:
            await event.reply(utils.premium_emoji(
                "❌ 𝗞𝗲𝘆 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ 𝗡𝗼 𝗸𝗲𝘆 𝗲𝘅𝗶𝘀𝘁𝘀 𝘄𝗶𝘁𝗵 𝘁𝗵𝗮𝘁 𝗜𝗗"
            ), parse_mode='html')
            return
        if row["revoked"]:
            await event.reply(utils.premium_emoji(
                "❌ 𝗞𝗲𝘆 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝘃𝗼𝗸𝗲𝗱\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ 𝗧𝗵𝗶𝘀 𝗸𝗲𝘆 𝗵𝗮𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗯𝗲𝗲𝗻 𝗿𝗲𝘃𝗼𝗸𝗲𝗱"
            ), parse_mode='html')
            return

        db.revoke_key(target)
        plan = row["plan"]
        created = time.strftime("%Y-%m-%d", time.localtime(row["created_at"]))
        status = "𝗨𝘀𝗲𝗱" if row["used_by"] else "𝗨𝗻𝘂𝘀𝗲𝗱"
        msg = (
            f"❌ 𝗞𝗲𝘆 𝗥𝗲𝘃𝗼𝗸𝗲𝗱\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"┣ 𝗞𝗲𝘆 ➜ <code>{target}</code>\n"
            f"┣ 𝗣𝗹𝗮𝗻 ➜ {plan}\n"
            f"┣ 𝗖𝗿𝗲𝗮𝘁𝗲𝗱 ➜ {created}\n"
            f"┣ 𝗦𝘁𝗮𝘁𝘂𝘀 ➜ {status}\n"
            f"┗ 𝗧𝗵𝗶𝘀 𝗸𝗲𝘆 𝗶𝘀 𝗻𝗼𝘄 𝗶𝗻𝘃𝗮𝗹𝗶𝗱"
        )
        await event.reply(utils.premium_emoji(msg), parse_mode='html')
