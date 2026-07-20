import time
import utils, database as db
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^/addplan(\s|$|@)'))
    async def add_plan(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            parts = event.text.split()
            target_id = int(parts[1])
            plan_input = parts[2].lower()

            plan_map = {'lite': 7, 'basic': 15, 'x': 30, 'rip': 0}
            if plan_input not in plan_map:
                raise Exception()

            plan = plan_input.upper()
            now = time.time()
            exp = 0 if plan_input == 'rip' else now + plan_map[plan_input] * 86400

            if db.is_premium(target_id):
                await event.reply(f"𝗨𝘀𝗲𝗿 {target_id} 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘀 𝗮𝗻 𝗮𝗰𝘁𝗶𝘃𝗲 𝗽𝗹𝗮𝗻")
                return

            db.add_premium(target_id, exp, plan)
            with utils._expiry_lock:
                utils._expiry_notified.discard(str(target_id))

            from utils import sbold
            tag = utils.get_role_tag(event.sender_id)
            res = (
                f"𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧\n"
                f"━━━━━━━━━━━━━\n"
                f"𝗧𝗮𝗿𝗴𝗲𝘁 𝗜𝗗: {target_id}\n"
                f"𝗔𝗰𝘁𝗶𝗼𝗻: {plan} 𝗣𝗹𝗮𝗻 𝗔𝗱𝗱𝗲𝗱\n"
                f"━━━━━━━━━━━━━\n"
                f"𝐔𝐬𝐞𝐫: {event.sender.first_name}{tag}"
            )
            await event.reply(res)
            try:
                await client.send_message(target_id,
                    f"{plan} 𝗣𝗹𝗮𝗻 𝗔𝗱𝗱𝗲𝗱\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"┣ 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 {plan} 𝗮𝗰𝗰𝗲𝘀𝘀\n"
                    f"┗ 𝗘𝗻𝗷𝗼𝘆 𝘂𝗻𝗹𝗶𝗺𝗶𝘁𝗲𝗱 𝗰𝗵𝗲𝗰𝗸𝘀")
            except:
                pass
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /addplan <userid> <plan> (lite/basic/x/rip)")
