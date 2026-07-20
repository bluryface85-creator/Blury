from telethon import events
import utils, database as db
from utils import sbold

def register(client):
    @client.on(events.NewMessage(pattern=r'^/leaderboard(\s|$|@)'))
    async def leaderboard_cmd(event):
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        if utils.is_banned(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗕𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return
        utils.add_user(event.sender_id)
        top = db.get_top_users("approved", 10)
        if not top:
            await event.reply("𝗡𝗼 𝗸𝗮𝗿𝗱𝗲𝗿𝘀 𝘆𝗲𝘁")
            return
        lines = []
        for i, (uid, count) in enumerate(top, 1):
            try:
                user = await client.get_entity(uid)
                fname = user.first_name or str(uid)
            except:
                fname = str(uid)
            name = f"<a href=\"tg://user?id={uid}\">{utils.sbold(fname)}</a>"
            lines.append(f"{i}. {name} ({count} charged)")
        text = (
            "𝗧𝗼𝗽 𝗞𝗮𝗿𝗱𝗲𝗿𝘀\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{chr(10).join(lines)}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await event.reply(utils.premium_emoji(text), parse_mode='html')
