import time
import utils, database as db
from telethon import events

PLAN_DURATION = {"LITE": 7, "BASIC": 15, "X": 30, "RIP": 0}

def register(client):
    @client.on(events.NewMessage(pattern=r'^/redeem(\s|$|@)'))
    async def redeem_key(event):
        uid = event.sender_id
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        if utils.is_banned(uid):
            return
        try:
            key = event.text.split()[1].strip()
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /redeem <key>")
            return

        result = db.redeem_key(key, uid)
        if result == "invalid":
            await event.reply(utils.premium_emoji(
                "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗞𝗲𝘆\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ 𝗧𝗵𝗲 𝗸𝗲𝘆 𝘆𝗼𝘂 𝗲𝗻𝘁𝗲𝗿𝗲𝗱 𝗱𝗼𝗲𝘀 𝗻𝗼𝘁 𝗲𝘅𝗶𝘀𝘁"
            ), parse_mode='html')
        elif result == "used":
            await event.reply(utils.premium_emoji(
                "❌ 𝗞𝗲𝘆 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗨𝘀𝗲𝗱\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ 𝗧𝗵𝗶𝘀 𝗸𝗲𝘆 𝗵𝗮𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗯𝗲𝗲𝗻 𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱"
            ), parse_mode='html')
        elif result == "revoked":
            await event.reply(utils.premium_emoji(
                "❌ 𝗞𝗲𝘆 𝗥𝗲𝘃𝗼𝗸𝗲𝗱\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ 𝗧𝗵𝗶𝘀 𝗸𝗲𝘆 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝘃𝗼𝗸𝗲𝗱 𝗯𝘆 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻"
            ), parse_mode='html')
        else:
            plan, custom_days = result
            from utils import sbold
            PLAN_RANK = {"LITE": 1, "BASIC": 2, "X": 3, "RIP": 4}
            if db.is_premium(uid):
                current_plan = (db.get_premium_plan(uid) or "").upper()
                if current_plan == plan:
                    await event.reply(utils.premium_emoji(
                        f"❌ 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗔𝗰𝘁𝗶𝘃𝗲\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"╰ 𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 {sbold(plan)} 𝗮𝗰𝘁𝗶𝘃𝗲"
                    ), parse_mode='html')
                    return
                if PLAN_RANK.get(current_plan, 0) >= PLAN_RANK.get(plan, 0):
                    await event.reply(utils.premium_emoji(
                        f"❌ 𝗕𝗲𝘁𝘁𝗲𝗿 𝗣𝗹𝗮𝗻 𝗔𝗰𝘁𝗶𝘃𝗲\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"╰ 𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 {sbold(current_plan)} 𝘄𝗵𝗶𝗰𝗵 𝗶𝘀 𝗯𝗲𝘁𝘁𝗲𝗿 𝘁𝗵𝗮𝗻 {sbold(plan)}"
                    ), parse_mode='html')
                    return
            duration_days = PLAN_DURATION[plan] if custom_days is None else custom_days
            exp = 0 if duration_days == 0 else time.time() + duration_days * 86400
            db.add_premium(uid, exp, plan)
            with utils._expiry_lock:
                utils._expiry_notified.discard(str(uid))

            days_str = "𝗟𝗶𝗳𝗲𝘁𝗶𝗺𝗲" if duration_days == 0 else f"{duration_days}"
            exp_str = "𝗟𝗶𝗳𝗲𝘁𝗶𝗺𝗲" if exp == 0 else time.strftime("%Y-%m-%d", time.localtime(exp))
            msg = (
                f"𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝘼𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙 🔥\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 𝗣𝗹𝗮𝗻 ➜ {sbold(plan)}\n"
                f"┣ 𝗗𝗮𝘆𝘀 ➜ {days_str}\n"
                f"┗ 𝗘𝘅𝗽𝗶𝗿𝘆 ➜ {exp_str}"
            )
            await event.reply(utils.premium_emoji(msg), parse_mode='html')
