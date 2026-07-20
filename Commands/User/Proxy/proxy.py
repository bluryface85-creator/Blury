import threading, requests, time
from telethon import events
import utils, database as db

def test_single_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    if not proxy_str:
        return False
    fp = utils.format_proxy(proxy_str)
    if not fp:
        return False
    try:
        proxy_url = f"http://{fp}"
        proxy_dict = {"http": proxy_url, "https": proxy_url}
        r = requests.get("http://ip-api.com/json", proxies=proxy_dict, timeout=20)
        return r.status_code == 200
    except:
        return False

def register(client):
    @client.on(events.NewMessage(pattern=r'^/proxy(\s|$|@)'))
    async def proxy_command(event):
        uid = event.sender_id
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        if event.is_group:
            await event.reply("╰ 𝙐𝙨𝙚 𝙞𝙣 𝙋𝙧𝙞𝙫𝙖𝙩𝙚 𝙩𝙤 𝙢𝙖𝙣𝙖𝙜𝙚 𝙥𝙧𝙤𝙭𝙮")
            return
        args = event.text.split(maxsplit=2)
        if len(args) < 2:
            await event.reply(
                "⋆ 𝗣𝗿𝗼𝘅𝘆 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "▸ /proxy add <proxy>\n"
                "▸ /proxy list\n"
                "▸ /proxy test\n"
                "▸ /proxy remove <index/all>\n"
                "━━━━━━━━━━━━━━━━━━━━")
            return
        cmd = args[1].lower()
        if not utils.is_admin(uid) and not utils.is_premium(uid):
            await event.reply(utils.premium_emoji(
                "𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙊𝙣𝙡𝙮 👻\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "╰ 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙨 𝙖 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙥𝙡𝙖𝙣.\n"
                "╰ 𝘽𝙪𝙮 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙋𝙡𝙖𝙣"
            ), parse_mode='html')
            return
        if cmd == "add":
            if len(args) < 3:
                await event.reply("𝙐𝙨𝙖𝙜𝙚: /proxy add <proxy>")
                return
            proxies = [l.strip() for l in args[2].split("\n") if l.strip()]
            if not proxies:
                await event.reply("𝗡𝗼 𝗽𝗿𝗼𝘅𝗶𝗲𝘀 𝗳𝗼𝘂𝗻𝗱!")
                return
            invalid = [p for p in proxies if not utils.is_valid_proxy_format(p)]
            if invalid:
                await event.reply(
                    "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗣𝗿𝗼𝘅𝘆 𝗙𝗼𝗿𝗺𝗮𝘁\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "┣ 𝗦𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱 𝗳𝗼𝗿𝗺𝗮𝘁𝘀:\n"
                    "┣ ip:port\n"
                    "┣ ip:port:user:pass\n"
                    "┣ user:pass@ip:port\n"
                    "┣ http://ip:port\n"
                    "┣ socks5://ip:port\n"
                    f"┗ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱: {invalid[0]}")
                return
            current_count = len(db.get_all_proxies())
            can_add = max(0, config.PROXY_LIMIT - current_count)
            if can_add == 0:
                await event.reply(f"𝗣𝗿𝗼𝘅𝘆 𝗟𝗶𝗺𝗶𝘁 𝗥𝗲𝗮𝗰𝗵𝗲𝗱\n━━━━━━━━━━━━━━━━━━━━\n╰ 𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 {current_count}/{config.PROXY_LIMIT} 𝗽𝗿𝗼𝘅𝗶𝗲𝘀.")
                return
            if len(proxies) > can_add:
                await event.reply(f"𝗣𝗿𝗼𝘅𝘆 𝗟𝗶𝗺𝗶𝘁\n━━━━━━━━━━━━━━━━━━━━\n╰ 𝗢𝗻𝗹𝘆 {can_add} 𝗼𝘂𝘁 𝗼𝗳 {len(proxies)} 𝘄𝗶𝗹𝗹 𝗯𝗲 𝘁𝗲𝘀𝘁𝗲𝗱 (𝗺𝗮𝘅 {config.PROXY_LIMIT}).")
                proxies = proxies[:can_add]
            msg = await event.reply(f"𝗧𝗲𝘀𝘁𝗶𝗻𝗴 {len(proxies)} 𝗽𝗿𝗼𝘅𝗶𝗲𝘀...")
            results = {"working": [], "dead": [], "dup": [], "invalid": []}
            lock = threading.Lock()
            def test_and_add(p):
                if test_single_proxy(p):
                    added = db.add_proxy(p)
                    with lock:
                        if added is False:
                            results["dup"].append(p)
                        else:
                            results["working"].append(p)
                else:
                    with lock: results["dead"].append(p)
            threads = []
            for p in proxies:
                t = threading.Thread(target=test_and_add, args=(p,))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            utils.load_proxies()
            total = len(proxies)
            w = len(results["working"])
            d = len(results["dead"])
            dup = len(results["dup"])
            inv = len(results["invalid"])
            try:
                await client.edit_message(event.chat_id, msg.id,
                    "𝗣𝗿𝗼𝘅𝘆 𝗔𝗱𝗱 𝗥𝗲𝘀𝘂𝗹𝘁\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"┣ 𝗧𝗼𝘁𝗮𝗹 ➜ {total}\n"
                    f"┣ 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 ➜ {w}\n"
                    f"┣ 𝗗𝘂𝗽𝗹𝗶𝗰𝗮𝘁𝗲 ➜ {dup}\n"
                    f"┣ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 ➜ {inv}\n"
                    f"┗ 𝗗𝗲𝗮𝗱 ➜ {d}")
            except:
                pass
        elif cmd == "list":
            proxies = db.get_all_proxies()
            if not proxies:
                await event.reply("𝗡𝗼 𝗽𝗿𝗼𝘅𝗶𝗲𝘀 𝗳𝗼𝘂𝗻𝗱.")
                return
            lines = []
            for i, p in enumerate(proxies, 1):
                lines.append(f"▸ {i}. {p}")
            text = "⋆ 𝗣𝗿𝗼𝘅𝘆 𝗟𝗶𝘀𝘁\n━━━━━━━━━━━━━━━━━\n" + "\n".join(lines) + f"\n━━━━━━━━━━━━━━━━━\n𝗧𝗼𝘁𝗮𝗹: {len(proxies)}"
            await event.reply(text)
        elif cmd == "test":
            proxies = db.get_all_proxies()
            if not proxies:
                await event.reply("𝗡𝗼 𝗽𝗿𝗼𝘅𝗶𝗲𝘀 𝘁𝗼 𝘁𝗲𝘀𝘁.")
                return
            msg = await event.reply(f"𝗧𝗲𝘀𝘁𝗶𝗻𝗴 {len(proxies)} 𝗽𝗿𝗼𝘅𝗶𝗲𝘀...")
            results = {"working": [], "dead": []}
            lock = threading.Lock()
            def test_one(p):
                if test_single_proxy(p):
                    with lock: results["working"].append(p)
                else:
                    with lock: results["dead"].append(p)
            threads = []
            for p in proxies:
                t = threading.Thread(target=test_one, args=(p,))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            if results["dead"]:
                for p in results["dead"]:
                    rows = db.get_conn().execute("SELECT id FROM proxies WHERE proxy = ?", (p,)).fetchone()
                    if rows:
                        db.remove_proxy_by_id(rows["id"])
            utils.load_proxies()
            res = (
                f"⋆ 𝗣𝗿𝗼𝘅𝘆 𝗧𝗲𝘀𝘁 𝗥𝗲𝘀𝘂𝗹𝘁\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"▸ 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 : {len(results['working'])}\n"
                f"▸ 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗗𝗲𝗮𝗱 : {len(results['dead'])}\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            try:
                await client.edit_message(event.chat_id, msg.id, res)
            except:
                await client.send_message(uid, res)
        elif cmd == "remove":
            proxies = db.get_all_proxies()
            if not proxies:
                await event.reply("𝗡𝗼 𝗽𝗿𝗼𝘅𝗶𝗲𝘀 𝘁𝗼 𝗿𝗲𝗺𝗼𝘃𝗲.")
                return
            if len(args) < 3:
                await event.reply("𝙐𝙨𝙖𝙜𝙚: /proxy remove <index/all>")
                return
            target = args[2].strip().lower()
            if target == "all":
                db.remove_all_proxies()
                utils.load_proxies()
                await event.reply("✓ 𝗔𝗹𝗹 𝗽𝗿𝗼𝘅𝗶𝗲𝘀 𝗿𝗲𝗺𝗼𝘃𝗲𝗱.")
            elif target.isdigit():
                idx = int(target) - 1
                if idx < 0 or idx >= len(proxies):
                    await event.reply("✗ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗶𝗻𝗱𝗲𝘅.")
                    return
                rows = db.get_conn().execute("SELECT id FROM proxies WHERE proxy = ?", (proxies[idx],)).fetchone()
                if rows:
                    db.remove_proxy_by_id(rows["id"])
                    utils.load_proxies()
                    await event.reply(f"✓ 𝗣𝗿𝗼𝘅𝘆 #{idx+1} 𝗿𝗲𝗺𝗼𝘃𝗲𝗱.")
            else:
                await event.reply("✗ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗮𝗿𝗴𝘂𝗺𝗲𝗻𝘁. 𝗨𝘀𝗲 𝗮 𝗻𝘂𝗺𝗯𝗲𝗿 𝗼𝗿 '𝗮𝗹𝗹'.")
        else:
            await event.reply("✗ 𝗨𝗻𝗸𝗻𝗼𝘄𝗻 𝗰𝗼𝗺𝗺𝗮𝗻𝗱. 𝗨𝘀𝗲: 𝗮𝗱𝗱, 𝗹𝗶𝘀𝘁, 𝘁𝗲𝘀𝘁, 𝗿𝗲𝗺𝗼𝘃𝗲")
