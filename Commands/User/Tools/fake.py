import requests, html
from telethon import events, Button
import utils, config
from Commands.Admin.plan import get_user_plan, PLANS

def register(client):
    @client.on(events.NewMessage(pattern=r'^/fake(\s|$|@)'))
    async def fake_command(event):
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
            await event.reply("𝗨𝘀𝗮𝗴𝗲\n━━━━━━━━━━━━━━━━━━━━\n┗ /fake <country_code>\n┣ 𝗘𝘅: /fake 𝘂𝘀")
            return

        country_code = args[1].lower()

        try:
            r = requests.get(f"https://randomuser.me/api/?nat={country_code}", timeout=10)
            if r.status_code != 200:
                await event.reply("𝗔𝗣𝗜 𝗘𝗿𝗿𝗼𝗿\n━━━━━━━━━━━━━━━━━━━━\n┗ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗳𝗲𝘁𝗰𝗵 𝗳𝗮𝗸𝗲 𝗶𝗻𝗳𝗼.")
                return

            data = r.json()
            if not data.get('results'):
                await event.reply("𝗡𝗼 𝗥𝗲𝘀𝘂𝗹𝘁𝘀\n━━━━━━━━━━━━━━━━━━━━\n┗ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗰𝗼𝘂𝗻𝘁𝗿𝘆 𝗰𝗼𝗱𝗲 𝗼𝗿 𝗻𝗼 𝗿𝗲𝘀𝘂𝗹𝘁𝘀 𝗳𝗼𝘂𝗻𝗱.")
                return

            u = data['results'][0]
            first_name = u['name']['first']
            last_name = u['name']['last']
            full_name = f"{first_name} {last_name}"
            gender = u['gender'].capitalize()
            street = f"{u['location']['street']['number']} {u['location']['street']['name']}"
            city = u['location']['city']
            state = u['location']['state']
            postcode = u['location']['postcode']
            country = u['location']['country']
            phone = u['phone']
            email = u['email']

            plan_type, plan_name, expiry, _ = get_user_plan(uid)
            plan_display = PLANS[plan_type]['display'] if plan_type else '𝗨𝗦𝗘𝗥'
            fname = (event.sender.first_name or "").replace('[', '').replace(']', '')

            text = (
                "𝗙𝗮𝗸𝗲 𝗜𝗻𝗳𝗼 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆\n"
                "━━━━━━━━━━━━━\n"
                f"✘ 𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲 : {full_name}\n"
                f"✘ 𝗚𝗲𝗻𝗱𝗲𝗿 : {gender}\n"
                f"✘ 𝗦𝘁𝗿𝗲𝗲𝘁 : {street}\n"
                f"✘ 𝗖𝗶𝘁𝘆 : {city}\n"
                f"✘ 𝗦𝘁𝗮𝘁𝗲 : {state}\n"
                f"✘ 𝗣𝗼𝘀𝘁𝗰𝗼𝗱𝗲 : {postcode}\n"
                f"✘ 𝗣𝗵𝗼𝗻𝗲 : {phone}\n"
                f"✘ 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country}\n"
                f"✘ 𝗘𝗺𝗮𝗶𝗹 : {email}\n"
                "━━━━━━━━━━━━━\n"
                f"𝗨𝘀𝗲𝗿 : <a href=\"tg://user?id={uid}\">{html.escape(utils.sbold(fname))}</a> [{plan_display}]"
            )
            keyboard = [
                [Button.inline("𝗥𝗲-𝗚𝗲𝗻", f"fake_regen_{country_code}", style='success'),
                 Button.inline("𝗘𝘅𝗶𝘁", "close_message", style='danger')]
            ]
            await event.reply(text, buttons=keyboard, parse_mode='html')

        except Exception as e:
            await event.reply(f"𝗘𝗿𝗿𝗼𝗿\n━━━━━━━━━━━━━━━━━━━━\n┗ {str(e)}")

    @client.on(events.CallbackQuery(pattern=b'^fake_regen_'))
    async def fake_regen_callback(event):
        uid = event.sender_id
        country_code = event.data.decode().split('_', 2)[2]
        fname = (event.sender.first_name or "").replace('[', '').replace(']', '')
        plan_type, plan_name, expiry, _ = get_user_plan(uid)
        plan_display = PLANS[plan_type]['display'] if plan_type else '𝗨𝗦𝗘𝗥'
        try:
            r = requests.get(f"https://randomuser.me/api/?nat={country_code}", timeout=10)
            if r.status_code != 200:
                await event.answer("𝗔𝗣𝗜 𝗘𝗿𝗿𝗼𝗿")
                return
            data = r.json()
            if not data.get('results'):
                await event.answer("𝗡𝗼 𝗥𝗲𝘀𝘂𝗹𝘁𝘀")
                return
            u = data['results'][0]
            first_name = u['name']['first']
            last_name = u['name']['last']
            full_name = f"{first_name} {last_name}"
            gender = u['gender'].capitalize()
            street = f"{u['location']['street']['number']} {u['location']['street']['name']}"
            city = u['location']['city']
            state = u['location']['state']
            postcode = u['location']['postcode']
            country = u['location']['country']
            phone = u['phone']
            email = u['email']
            text = (
                "𝗙𝗮𝗸𝗲 𝗜𝗻𝗳𝗼 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆\n"
                "━━━━━━━━━━━━━\n"
                f"✘ 𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲 : {full_name}\n"
                f"✘ 𝗚𝗲𝗻𝗱𝗲𝗿 : {gender}\n"
                f"✘ 𝗦𝘁𝗿𝗲𝗲𝘁 : {street}\n"
                f"✘ 𝗖𝗶𝘁𝘆 : {city}\n"
                f"✘ 𝗦𝘁𝗮𝘁𝗲 : {state}\n"
                f"✘ 𝗣𝗼𝘀𝘁𝗰𝗼𝗱𝗲 : {postcode}\n"
                f"✘ 𝗣𝗵𝗼𝗻𝗲 : {phone}\n"
                f"✘ 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country}\n"
                f"✘ 𝗘𝗺𝗮𝗶𝗹 : {email}\n"
                "━━━━━━━━━━━━━\n"
                f"𝗨𝘀𝗲𝗿 : <a href=\"tg://user?id={uid}\">{html.escape(utils.sbold(fname))}</a> [{plan_display}]"
            )
            keyboard = [
                [Button.inline("𝗥𝗲-𝗚𝗲𝗻", f"fake_regen_{country_code}", style='success'),
                 Button.inline("𝗘𝘅𝗶𝘁", "close_message", style='danger')]
            ]
            try:
                await event.edit(text, buttons=keyboard, parse_mode='html')
            except:
                await client.edit_message(event.chat_id, event.message_id, text, buttons=keyboard, parse_mode='html')
        except Exception as e:
            await event.answer(str(e))
        await event.answer()
