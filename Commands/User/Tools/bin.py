import requests, html
from telethon import Button, events
import utils
import config
from Commands.Admin.plan import get_user_plan, PLANS

def check_bin(bin_number):
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=5)
        if r.status_code == 200:
            return r.json(), None
        elif r.status_code == 404:
            return None, "✘ 𝗕𝗜𝗡 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲"
        else:
            return None, f"✘ 𝗔𝗣𝗜 𝗲𝗿𝗿𝗼𝗿: {r.status_code}"
    except Exception as e:
        return None, f"✘ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗳𝗮𝗶𝗹𝗲𝗱: {str(e)}"

def register(client):
    @client.on(events.NewMessage(pattern=r'^/bin(\s|$|@)'))
    async def bin_command(event):
        uid = event.sender_id
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        if utils.is_banned(uid):
            await event.reply("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗕𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return
        utils.add_user(uid)

        args = event.text.split()
        if len(args) < 2:
            await event.reply("𝙐𝙨𝙖𝙜𝙚\n━━━━━━━━━━━━━━━━━━━━\n\n┗ `/bin <bin>`", parse_mode="Markdown")
            return

        bin_number = args[1]
        if not bin_number.isdigit() or len(bin_number) < 6:
            await event.reply("𝙀𝙧𝙧𝙤𝙧\n━━━━━━━━━━━━━━━━━━━━\n\n┗ 𝗣𝗿𝗼𝘃𝗶𝗱𝗲 𝗮 𝘃𝗮𝗹𝗶𝗱 𝟲-𝗱𝗶𝗴𝗶𝘁 𝗼𝗿 𝗹𝗼𝗻𝗴𝗲𝗿 𝗕𝗜𝗡.")
            return

        waiting = await event.reply("┣ 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴\n━━━━━━━━━━━━━━━\n┣ 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗕𝗜𝗡...")

        data, error = check_bin(bin_number[:6])

        if error:
            try: await client.delete_messages(event.chat_id, [waiting.id])
            except: pass
            await event.reply(f"𝙀𝙧𝙧𝙤𝙧\n━━━━━━━━━━━━━━━━━━━━\n\n┗ {error}")
            return

        bin_val = data.get('bin', 'None')
        bank = data.get('bank', '{}')
        brand = data.get('brand', 'None')
        level = data.get('level', 'None')
        card_type = data.get('type', '/')
        country = data.get('country_name', '{}')
        country_flag = data.get('country_flag', '')

        scheme = brand if level in ('None', 'UNKNOWN', '', 'N/A') else f"{brand} {level}"
        if scheme in ('None', 'N/A', ''):
            scheme = '/'

        plan_type, plan_name, expiry, _ = get_user_plan(uid)
        plan_display = PLANS[plan_type]['display'] if plan_type else '𝗨𝗦𝗘𝗥'
        fname = (event.sender.first_name or "").replace('[', '').replace(']', '')

        msg = (
            "𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"❯ 𝗕𝗜𝗡 : {bin_val}\n"
            f"❯ 𝗦𝗰𝗵𝗲𝗺𝗲 : {scheme}\n"
            f"❯ 𝗧𝘆𝗽𝗲 : {card_type}\n"
            f"❯ 𝗕𝗮𝗻𝗸 : {bank}\n"
            f"❯ 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {country_flag}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"𝗨𝘀𝗲𝗿 : <a href=\"tg://user?id={uid}\">{html.escape(utils.sbold(fname))}</a> [{plan_display}]"
        )

        keyboard = [
            [Button.inline("𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲", f"regen_{bin_val}_10", style='success'),
             Button.inline("𝗘𝘅𝗶𝘁", "close_message", style='danger')]
        ]

        try: await client.delete_messages(event.chat_id, [waiting.id])
        except: pass
        await event.reply(msg, buttons=keyboard, parse_mode='html')
