import os, utils, config
from telethon import events

MAINT_FILE = os.path.join(config.DATA_DIR, "maintenance.txt")

def is_maintenance():
    try:
        with open(MAINT_FILE) as f:
            return f.read().strip() == "True"
    except:
        return False

def set_maintenance(state):
    os.makedirs(os.path.dirname(MAINT_FILE), exist_ok=True)
    with open(MAINT_FILE, "w") as f:
        f.write("True" if state else "False")

def register(client):
    @client.on(events.NewMessage(pattern=r'^/maintenance(\s|$|@)'))
    async def maintenance_cmd(event):
        if not utils.is_authorized(event):
            return
        if not utils.is_admin(event.sender_id):
            await event.reply("𝗬𝗼𝘂 𝗱𝗼𝗻𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!!")
            return
        args = event.text.split()
        if len(args) < 2 or args[1].lower() not in ("on", "off"):
            await event.reply("𝗨𝘀𝗮𝗴𝗲: /maintenance on/off")
            return
        state = args[1].lower() == "on"
        set_maintenance(state)
        await event.reply(f"✓ 𝗠𝗮𝗶𝗻𝘁𝗲𝗻𝗮𝗻𝗰𝗲 𝗺𝗼𝗱𝗲 𝗶𝘀 𝗻𝗼𝘄 {'𝗢𝗡' if state else '𝗢𝗙𝗙'}")

    @client.on(events.NewMessage(pattern=r'^/', func=lambda e: is_maintenance() and not utils.is_admin(e.sender_id)))
    async def maintenance_block(event):
        await event.reply("𝗠𝗮𝗶𝗻𝘁𝗲𝗻𝗮𝗻𝗰𝗲\n━━━━━━━━━━━━\n┗ 𝗕𝗼𝘁 𝗶𝘀 𝘂𝗻𝗱𝗲𝗿 𝗺𝗮𝗶𝗻𝘁𝗲𝗻𝗮𝗻𝗰𝗲. 𝗧𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗹𝗮𝘁𝗲𝗿.")
        raise events.StopPropagation
