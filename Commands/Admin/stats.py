import utils, database as db
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^/stats(\s|$|@)'))
    async def bot_stats(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return

        charged = db.get_stat("charged")
        approved = db.get_stat("approved")
        threeds = db.get_stat("3ds")
        declined = db.get_stat("declined")
        total_checks = charged + approved + threeds + declined

        premium = db.get_premium_count()
        users = db.get_total_users()
        banned = db.get_banned_count()

        tag = utils.get_role_tag(event.sender_id)
        res = (
            f"𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"▸ 𝗖𝗵𝗮𝗿𝗴𝗲𝗱 ━ {charged}\n"
            f"▸ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ━ {approved}\n"
            f"▸ 𝟯𝗗𝗦 ━ {threeds}\n"
            f"▸ 𝗟𝗶𝘃𝗲 ━ {approved + threeds}\n"
            f"▸ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ━ {declined}\n"
            f"▸ 𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗲𝗰𝗸𝘀 ━ {total_checks}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"▸ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 ━ {premium}\n"
            f"▸ 𝗨𝘀𝗲𝗿𝘀 ━ {users}\n"
            f"▸ 𝗕𝗮𝗻𝗻𝗲𝗱 ━ {banned}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        await event.reply(res)
