import re, html
from telethon import events
import utils, config
from utils import sbold

CONFIG_PATH = "config.py"

def _update_admin_ids(new_ids):
    with open(CONFIG_PATH, encoding='utf-8') as f:
        content = f.read()
    ids_str = ", ".join(str(i) for i in sorted(new_ids))
    content = re.sub(
        r'^ADMIN_IDS\s*=\s*\[.*?\]',
        f'ADMIN_IDS = [{ids_str}]',
        content,
        count=1,
        flags=re.MULTILINE
    )
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    import config
    config.ADMIN_IDS = new_ids

async def _user_line(client, uid):
    try:
        entity = await client.get_entity(uid)
        name = html.escape(sbold(entity.first_name or str(uid)))
    except:
        name = sbold(str(uid))
    return f'<a href="tg://user?id={uid}">{name}</a>{utils.get_role_tag(uid)}'

def register(client):
    @client.on(events.NewMessage(pattern=r'^/addadmin(\s|$|@)'))
    async def add_admin(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            target = int(event.text.split()[1])
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /addadmin <userid>")
            return
        if target in config.ADMIN_IDS:
            await event.reply(f"╰ 𝗨𝘀𝗲𝗿 {target} 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻")
            return
        ids = list(config.ADMIN_IDS)
        ids.append(target)
        _update_admin_ids(ids)
        user_line = await _user_line(client, target)
        by_line = await _user_line(client, event.sender_id)
        await event.reply(
            f"𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱𝗲𝗱\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"╰ 𝗨𝘀𝗲𝗿: {user_line}\n"
            f"╰ 𝗕𝘆: {by_line}",
            parse_mode='html')
        try:
            await client.send_message(target,
                f"𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱𝗲𝗱\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"╰ 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 𝗮𝗱𝗺𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀 𝗯𝘆 {by_line}",
                parse_mode='html')
        except:
            pass

    @client.on(events.NewMessage(pattern=r'^/rmadmin(\s|$|@)'))
    async def rm_admin(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        try:
            target = int(event.text.split()[1])
        except:
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /rmadmin <userid>")
            return
        if target not in config.ADMIN_IDS:
            await event.reply(f"╰ 𝗨𝘀𝗲𝗿 {target} 𝗶𝘀 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻")
            return
        ids = list(config.ADMIN_IDS)
        ids.remove(target)
        _update_admin_ids(ids)
        user_line = await _user_line(client, target)
        by_line = await _user_line(client, event.sender_id)
        await event.reply(
            f"𝗔𝗱𝗺𝗶𝗻 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"╰ 𝗨𝘀𝗲𝗿: {user_line}\n"
            f"╰ 𝗕𝘆: {by_line}",
            parse_mode='html')
        try:
            await client.send_message(target,
                f"𝗔𝗱𝗺𝗶𝗻 𝗥𝗲𝗺𝗼𝘃𝗲𝗱\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"╰ 𝗬𝗼𝘂𝗿 𝗮𝗱𝗺𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝘃𝗼𝗸𝗲𝗱 𝗯𝘆 {by_line}",
                parse_mode='html')
        except:
            pass
