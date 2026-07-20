import utils, database as db
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^/unban(\s|$|@)'))
    async def unban_user(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            target_id = int(event.text.split()[1])
            db.remove_ban(target_id)
            tag = utils.get_role_tag(event.sender_id)
            res = (
                f"𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧\n"
                f"━━━━━━━━━━━━━\n"
                f"𝗧𝗮𝗿𝗴𝗲𝘁 𝗜𝗗: {target_id}\n"
                f"𝗔𝗰𝘁𝗶𝗼𝗻: 𝗨𝗻𝗯𝗮𝗻 𝗨𝘀𝗲𝗿\n"
                f"𝗡𝗲𝘄 𝗥𝗮𝗻𝗸: [𝗙𝗥𝗘𝗘]\n"
                f"━━━━━━━━━━━━━\n"
                f"𝐔𝐬𝐞𝐫: {event.sender.first_name}{tag}"
            )
            await event.reply(res)
            try:
                await client.send_message(target_id,
                    "𝗡𝗼𝘁𝗶𝗰𝗲: 𝗬𝗼𝘂𝗿 𝗯𝗮𝗻 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱. 𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗮𝗴𝗮𝗶𝗻.")
            except:
                pass
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /unban <userid>")
