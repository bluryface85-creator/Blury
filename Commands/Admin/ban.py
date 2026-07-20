import time
import utils, database as db
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^/ban(\s|$|@)'))
    async def ban_user(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            parts = event.text.split()
            target_id = int(parts[1])
            duration = parts[2] if len(parts) > 2 else 'lifetime'
            now = time.time()
            if duration == 'lifetime': exp = 0
            elif duration.endswith('s'): exp = now + int(duration[:-1])
            elif duration.endswith('m'): exp = now + int(duration[:-1]) * 60
            elif duration.endswith('h'): exp = now + int(duration[:-1]) * 3600
            elif duration.endswith('d'): exp = now + int(duration[:-1]) * 86400
            else: raise Exception()

            db.add_ban(target_id, exp)
            dur_label = "Lifetime" if duration == 'lifetime' else duration.upper()
            tag = utils.get_role_tag(event.sender_id)
            res = (
                f"𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧\n"
                f"━━━━━━━━━━━━━\n"
                f"𝗧𝗮𝗿𝗴𝗲𝘁 𝗜𝗗: {target_id}\n"
                f"𝗔𝗰𝘁𝗶𝗼𝗻: 𝗕𝗮𝗻 𝗨𝘀𝗲𝗿\n"
                f"𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {dur_label}\n"
                f"𝗡𝗲𝘄 𝗥𝗮𝗻𝗸: [𝗕𝗔𝗡𝗡𝗘𝗗]\n"
                f"━━━━━━━━━━━━━\n"
                f"𝐔𝐬𝐞𝐫: {event.sender.first_name}{tag}"
            )
            await event.reply(res)
            try:
                await client.send_message(target_id,
                    f"𝗡𝗼𝘁𝗶𝗰𝗲: 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗕𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁 𝗳𝗼𝗿 {dur_label}. 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗼𝘂𝗿 𝗮𝗱𝗺𝗶𝗻 𝗶𝗳 𝘁𝗵𝗶𝘀 𝗶𝘀 𝗮 𝗺𝗶𝘀𝘁𝗮𝗸𝗲.")
            except:
                pass
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /ban <userid> <duration>")
