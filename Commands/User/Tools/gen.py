import random, time, io, requests, html
from telethon import Button, events
import utils, config
from Commands.Admin.plan import get_user_plan, PLANS

def luhn_verification(num):
    num = [int(d) for d in str(num)]
    check_digit = num.pop()
    num.reverse()
    total = 0
    for i, digit in enumerate(num):
        if i % 2 == 0:
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        total += digit
    return (total * 9) % 10 == check_digit

def generate_checksum(partial_num):
    partial_num = [int(d) for d in str(partial_num)]
    partial_num.reverse()
    total = 0
    for i, digit in enumerate(partial_num):
        if i % 2 == 0:
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        total += digit
    return (total * 9) % 10

def cc_gen(bin_data, amount):
    parts = bin_data.split('|')
    bin_num = parts[0]
    month = parts[1] if len(parts) > 1 else 'Rn'
    year = parts[2] if len(parts) > 2 else 'Rn'
    cvv = parts[3] if len(parts) > 3 else 'Rn'
    bin_num = ''.join(filter(str.isdigit, bin_num))

    generated_cards = []
    length = 15 if bin_num.startswith('34') or bin_num.startswith('37') else 16
    start_time = time.time()

    for _ in range(amount):
        for _ in range(20):
            curr_len = len(bin_num)
            needed_random = length - curr_len - 1
            if needed_random < 0:
                pan_partial = bin_num[:length-1]
            else:
                pan_partial = bin_num + ''.join([str(random.randint(0, 9)) for _ in range(needed_random)])
            checksum = generate_checksum(pan_partial)
            pan = pan_partial + str(checksum)
            if luhn_verification(pan):
                break

        curr_year = int(time.strftime("%Y"))
        curr_month = int(time.strftime("%m"))

        g_year = year
        if g_year == 'Rn' or not g_year.isdigit():
            g_year = str(random.randint(curr_year, curr_year + 5))
        elif len(g_year) == 2:
            g_year = "20" + g_year

        g_month = month
        if g_month == 'Rn' or not g_month.isdigit():
            min_month = curr_month if int(g_year) == curr_year else 1
            g_month = f"{random.randint(min_month, 12):02d}"
        else:
            g_month = f"{int(g_month):02d}"

        if int(g_year) < curr_year or (int(g_year) == curr_year and int(g_month) < curr_month):
            g_year = str(curr_year)
            g_month = f"{random.randint(curr_month, 12):02d}"

        g_cvv = cvv
        if g_cvv == 'Rn' or not g_cvv.isdigit():
            cvv_len = 4 if length == 15 else 3
            g_cvv = ''.join([str(random.randint(0, 9)) for _ in range(cvv_len)])

        generated_cards.append(f"{pan}|{g_month}|{g_year}|{g_cvv}")

    return generated_cards, time.time() - start_time

def get_bin_info(bin_number):
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def register(client):
    @client.on(events.NewMessage(pattern=r'^/gen(\s|$|@)'))
    async def gen_command(event):
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
        usage = (
            "𝙐𝙨𝙖𝙜𝙚\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "┗ `/gen <bin>`\n\n"
            "𝗘𝘅𝗮𝗺𝗽𝗹𝗲𝘀:\n"
            "┣ `/gen 447697`\n"
            "┣ `/gen 447697|12|2026`\n"
            "┣ `/gen 447697|rnd|2026|123`\n"
            "┗ `/gen 447697 10`"
        )

        if len(args) < 2:
            await event.reply(usage, parse_mode="Markdown")
            return

        bin_input = args[1].strip().rstrip('|')
        if not bin_input or not any(c.isdigit() for c in bin_input.split('|')[0]):
            await event.reply(
                "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗖𝗮𝗿𝗱 𝗙𝗼𝗿𝗺𝗮𝘁\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┣ 𝗘𝘅𝗮𝗺𝗽𝗹𝗲𝘀:\n"
                "┣ /gen 447697\n"
                "┣ /gen 447697|12|2026\n"
                "┣ /gen 447697|rnd|2026|123\n"
                "┗ /gen 447697 10")
            return

        amount = 10
        if len(args) > 2 and args[2].isdigit():
            amount = int(args[2])

        clean_bin = bin_input.split('|')[0][:6]
        cards, time_taken = cc_gen(bin_input, amount)
        bin_info = get_bin_info(clean_bin)

        bank = bin_info.get('bank', 'N/A')
        country = bin_info.get('country_name', 'N/A')
        flag = bin_info.get('country_flag', '')
        brand = bin_info.get('brand', 'N/A')
        level = bin_info.get('level', 'N/A')
        ctype = bin_info.get('type', 'N/A')

        full_scheme = brand if level in ('N/A', 'UNKNOWN', '', 'None') else f"{brand} {level}"

        plan_type, plan_name, expiry, _ = get_user_plan(uid)
        plan_display = PLANS[plan_type]['display'] if plan_type else '𝗨𝗦𝗘𝗥'
        fname = (event.sender.first_name or "").replace('[', '').replace(']', '')

        header = (
            "𝗖𝗮𝗿𝗱𝘀 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"❯ 𝗕𝗜𝗡 : {clean_bin}\n"
            f"❯ 𝗖𝗮𝗿𝗱𝘀 : {amount}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )

        footer = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"❯ 𝗦𝗰𝗵𝗲𝗺𝗲 : {full_scheme}\n"
            f"❯ 𝗧𝘆𝗽𝗲 : {ctype}\n"
            f"❯ 𝗕𝗮𝗻𝗸 : {bank}\n"
            f"❯ 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"𝗨𝘀𝗲𝗿 : <a href=\"tg://user?id={uid}\">{html.escape(utils.sbold(fname))}</a> [{plan_display}]"
        )

        keyboard = [
            [Button.inline("𝗥𝗲-𝗚𝗲𝗻", f"regen_{bin_input}_{amount}", style='success'),
             Button.inline("𝗘𝘅𝗶𝘁", "close_message", style='danger')]
        ]

        if amount <= 10:
            card_list = "\n".join([f"`{c}`" for c in cards])
            response_text = header + card_list + "\n" + footer
            await event.reply(response_text, buttons=keyboard, parse_mode='html')
        else:
            file_content = "\n".join(cards)
            file_bio = io.BytesIO(file_content.encode('utf-8'))
            file_bio.name = f"gen_{clean_bin}_{uid}.txt"
            caption = header + "𝗖𝗮𝗿𝗱𝘀 𝗶𝗻 𝗳𝗶𝗹𝗲 𝗮𝗯𝗼𝘃𝗲" + footer
            await client.send_file(event.chat_id, file_bio, caption=caption, buttons=keyboard)

    @client.on(events.CallbackQuery(pattern=b'^regen_'))
    async def regen_callback(event):
        parts = event.data.decode().split('_', 2)
        if len(parts) < 3:
            await event.answer("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗱𝗮𝘁𝗮")
            return
        bin_input = parts[1]
        amount = int(parts[2])

        uid = event.sender_id
        clean_bin = bin_input.split('|')[0][:6]
        cards, time_taken = cc_gen(bin_input, amount)
        bin_info = get_bin_info(clean_bin)

        bank = bin_info.get('bank', 'N/A')
        country = bin_info.get('country_name', 'N/A')
        flag = bin_info.get('country_flag', '')
        brand = bin_info.get('brand', 'N/A')
        level = bin_info.get('level', 'N/A')
        ctype = bin_info.get('type', 'N/A')
        full_scheme = brand if level in ('N/A', 'UNKNOWN', '', 'None') else f"{brand} {level}"

        plan_type, plan_name, expiry, _ = get_user_plan(uid)
        plan_display = PLANS[plan_type]['display'] if plan_type else '𝗨𝗦𝗘𝗥'
        fname = (event.sender.first_name or "").replace('[', '').replace(']', '')

        header = (
            "𝗖𝗮𝗿𝗱𝘀 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"❯ 𝗕𝗜𝗡 : {clean_bin}\n"
            f"❯ 𝗖𝗮𝗿𝗱𝘀 : {amount}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )
        footer = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"❯ 𝗦𝗰𝗵𝗲𝗺𝗲 : {full_scheme}\n"
            f"❯ 𝗧𝘆𝗽𝗲 : {ctype}\n"
            f"❯ 𝗕𝗮𝗻𝗸 : {bank}\n"
            f"❯ 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"𝗨𝘀𝗲𝗿 : <a href=\"tg://user?id={uid}\">{html.escape(utils.sbold(fname))}</a> [{plan_display}]"
        )

        keyboard = [
            [Button.inline("𝗥𝗲-𝗚𝗲𝗻", f"regen_{bin_input}_{amount}", style='success'),
             Button.inline("𝗘𝘅𝗶𝘁", "close_message", style='danger')]
        ]

        try:
            if amount <= 10:
                card_list = "\n".join([f"`{c}`" for c in cards])
                await client.edit_message(event.chat_id, event.message_id,
                    header + card_list + "\n" + footer,
                    buttons=keyboard, parse_mode='html')
            else:
                file_content = "\n".join(cards)
                file_bio = io.BytesIO(file_content.encode('utf-8'))
                file_bio.name = f"gen_{clean_bin}_{uid}.txt"
                await client.edit_message(event.chat_id, event.message_id, header + "𝗖𝗮𝗿𝗱𝘀 𝗶𝗻 𝗳𝗶𝗹𝗲 𝗮𝗯𝗼𝘃𝗲" + footer, buttons=keyboard)
                await client.send_file(event.chat_id, file_bio)
        except:
            pass
        await event.answer()

    @client.on(events.CallbackQuery(data=b'close_message'))
    async def close_callback(event):
        try:
            await client.delete_messages(event.chat_id, [event.message_id])
        except:
            pass
        await event.answer()
