import queue, threading, time, requests
from concurrent.futures import ThreadPoolExecutor
import database as db
import config

def is_authorized(event):
    if event.is_private:
        return True
    if event.is_group and event.chat_id == config.AUTHORIZED_GROUP:
        return True
    return False

def premium_emoji(text):
    if not text:
        return text
    placeholders = []
    result = text
    for i, (emoji, doc_id) in enumerate(config.PREMIUM_EMOJI_IDS.items()):
        placeholder = f"\x00PE{i:02d}\x00"
        placeholders.append((placeholder, doc_id, emoji))
        result = result.replace(emoji, placeholder)
    for placeholder, doc_id, emoji in placeholders:
        result = result.replace(placeholder, f'<tg-emoji emoji-id="{doc_id}">{emoji}</tg-emoji>')
    return result

def mbold(text):
    r = []
    for ch in text:
        if 'A' <= ch <= 'Z': r.append(chr(ord(ch) - ord('A') + 0x1D400))
        elif 'a' <= ch <= 'z': r.append(chr(ord(ch) - ord('a') + 0x1D41A))
        elif '0' <= ch <= '9': r.append(chr(ord(ch) - ord('0') + 0x1D7CE))
        else: r.append(ch)
    return ''.join(r)

def sbold(text):
    r = []
    for ch in text:
        if 'A' <= ch <= 'Z': r.append(chr(ord(ch) - ord('A') + 0x1D5D4))
        elif 'a' <= ch <= 'z': r.append(chr(ord(ch) - ord('a') + 0x1D5EE))
        elif '0' <= ch <= '9': r.append(chr(ord(ch) - ord('0') + 0x1D7EC))
        else: r.append(ch)
    return ''.join(r)

def format_hit_log(gateway, response, price, user_info, emoji="💎", label="CHARGED"):
    return (
        f"💳 ▶️ {sbold(label)} {emoji}\n"
        f"{sbold('Gateway')}: {sbold(gateway)}\n"
        f"{sbold('Price')}: {sbold(f'${price}')}\n"
        f"{sbold('Response')}: {sbold(response)}\n"
        f"{sbold('User')}: {user_info}"
    )

async def send_hit_log(client, log_text):
    if hasattr(config, 'LOGS_GROUP') and config.LOGS_GROUP:
        try:
            from telethon import Button
            await client.send_message(config.LOGS_GROUP, premium_emoji(log_text), parse_mode='html',
                buttons=[[Button.url(sbold("BLURY"), "https://t.me/Pussychkbot")]])
        except:
            pass

ADMIN_LIMIT = 10000
PREMIUM_LIMIT = 5000
FREE_LIMIT = 0
MAX_RETRIES = 3
WORKERS = 25

ACTIVE_JOBS = {}
ACTIVE_USERS_PP = {}
ACTIVE_USERS_MPP = {}
USER_ACTIVE_JOB = {}

PROXY_QUEUE = queue.Queue()
for p in db.get_all_proxies():
    PROXY_QUEUE.put(p)

def is_admin(user_id):
    return user_id in config.ADMIN_IDS

def is_premium(user_id):
    if is_admin(user_id): return True
    return db.is_premium(user_id)

def is_banned(user_id):
    return db.is_banned(user_id)

def add_user(user_id):
    db.add_user(user_id)

def get_role_tag(user_id):
    if is_admin(user_id): return " [𝗔𝗗𝗠𝗜𝗡]"
    if is_premium(user_id): return " [𝗣𝗥𝗘𝗠𝗜𝗨𝗠]"
    return " [𝗙𝗥𝗘𝗘]"

def get_stats():
    return db.get_all_stats()

def save_stats(stats):
    db.save_stats(stats)

def format_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    if not proxy_str: return None
    if '@' in proxy_str: return proxy_str
    parts = proxy_str.split(':')
    if len(parts) == 4:
        return f"{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return proxy_str

def get_proxy_dict():
    if PROXY_QUEUE.empty(): return None, None
    p = PROXY_QUEUE.get()
    fp = format_proxy(p)
    proxy_dict = None
    if not any(p.startswith(proto) for proto in ['http', 'socks']):
        proxy_dict = {"http": f"http://{fp}", "https": f"http://{fp}"}
    else:
        proxy_dict = {"http": fp, "https": fp}
    return proxy_dict, p

def release_proxy(p):
    if p: PROXY_QUEUE.put(p)

def load_proxies():
    with PROXY_QUEUE.mutex:
        PROXY_QUEUE.queue.clear()
    for p in db.get_all_proxies():
        PROXY_QUEUE.put(p)
    return PROXY_QUEUE.qsize()

def save_proxies(proxies):
    db.remove_all_proxies()
    for p in proxies:
        db.add_proxy(p)
    load_proxies()

def test_proxy(proxy_str):
    try:
        fp = format_proxy(proxy_str.strip())
        if not fp: return False
        scheme = "http"
        if any(proxy_str.strip().startswith(proto) for proto in ['http://', 'socks4://', 'socks5://']):
            scheme = proxy_str.strip().split('://')[0]
        proxy_dict = {"http": f"{scheme}://{fp}", "https": f"{scheme}://{fp}"}
        r = requests.get('http://ip-api.com/json', proxies=proxy_dict, timeout=20)
        return r.status_code == 200
    except:
        return False

def test_proxies_bulk(proxy_list, max_workers=50):
    res = {"working": [], "dead": [], "invalid": []}
    lock = threading.Lock()
    def test_one(p):
        if ':' not in p:
            with lock: res["invalid"].append(p)
            return
        if test_proxy(p):
            with lock: res["working"].append(p)
        else:
            with lock: res["dead"].append(p)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        ex.map(test_one, proxy_list)
    return res

_expiry_notified = set()
_ban_notified = set()
_expiry_lock = threading.Lock()
_ban_lock = threading.Lock()

def has_proxies():
    return db.get_conn().execute("SELECT COUNT(*) FROM proxies").fetchone()[0] > 0

def is_valid_proxy_format(proxy_str):
    p = proxy_str.strip()
    for prefix in ['http://', 'https://', 'socks4://', 'socks5://']:
        if p.startswith(prefix):
            p = p[len(prefix):]
            break
    if '@' in p:
        parts = p.split('@')
        if len(parts) != 2:
            return False
        auth, hostport = parts
        if ':' not in auth:
            return False
        hp = hostport.split(':')
        if len(hp) != 2:
            return False
        host, port = hp
        if not host or not port.isdigit():
            return False
        return True
    hp = p.split(':')
    if len(hp) == 2:
        host, port = hp
        return bool(host and port.isdigit())
    if len(hp) == 4:
        host, port, user, password = hp
        return bool(host and port.isdigit() and user and password)
    return False

async def check_expired_premiums(client):
    import asyncio
    await asyncio.sleep(5)
    while True:
        try:
            expired = db.get_expired_premiums()
            for uid in expired:
                with _expiry_lock:
                    if str(uid) in _expiry_notified: continue
                    _expiry_notified.add(str(uid))
                try:
                    await client.send_message(uid,
                        "𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗘𝘅𝗽𝗶𝗿𝗲𝗱\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "┣ 𝗬𝗼𝘂𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗽𝗹𝗮𝗻 𝗵𝗮𝘀 𝗲𝗻𝗱𝗲𝗱\n"
                        "┣ 𝗠𝗮𝘀𝘀 𝗰𝗵𝗲𝗰𝗸 𝗳𝗲𝗮𝘁𝘂𝗿𝗲 𝗶𝘀 𝗻𝗼𝘄 𝗹𝗼𝗰𝗸𝗲𝗱\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "┗ 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗔𝗗𝗠𝗜𝗡 𝘁𝗼 𝗿𝗲𝗻𝗲𝘄")
                except:
                    pass
            expired_bans = db.get_expired_bans()
            for uid in expired_bans:
                with _ban_lock:
                    if str(uid) in _ban_notified: continue
                    _ban_notified.add(str(uid))
                db.remove_ban(uid)
                try:
                    await client.send_message(uid,
                        "𝗕𝗮𝗻 𝗘𝘅𝗽𝗶𝗿𝗲𝗱\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "┣ 𝗬𝗼𝘂𝗿 𝗯𝗮𝗻 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗵𝗮𝘀 𝗲𝗻𝗱𝗲𝗱\n"
                        "┣ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘄 𝘂𝗻𝗯𝗮𝗻𝗻𝗲𝗱\n"
                        "┣ 𝗔𝗹𝗹 𝗯𝗼𝘁 𝗳𝗲𝗮𝘁𝘂𝗿𝗲𝘀 𝗮𝗿𝗲 𝘂𝗻𝗹𝗼𝗰𝗸𝗲𝗱\n"
                        "┗ 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘆𝗼𝘂𝗿 𝗽𝗮𝘁𝗶𝗲𝗻𝗰𝗲")
                except:
                    pass
        except:
            pass
        await asyncio.sleep(5)

async def check_membership(client, user_id):
    from telethon.errors import UserNotParticipantError
    missing = []
    try:
        await client.get_permissions(config.REQUIRED_CHANNEL, user_id)
    except UserNotParticipantError:
        missing.append("channel")
    except:
        missing.append("channel")
    try:
        await client.get_permissions(config.REQUIRED_GROUP_ID, user_id)
    except UserNotParticipantError:
        missing.append("group")
    except:
        missing.append("group")
    return missing

async def require_membership(client, event):
    if is_admin(event.sender_id):
        return True
    missing = await check_membership(client, event.sender_id)
    if not missing:
        return True
    from telethon import Button
    parts = []
    if "channel" in missing:
        parts.append("╰ 𝗖𝗵𝗮𝗻𝗻𝗲𝗹")
    if "group" in missing:
        parts.append("╰ 𝗚𝗿𝗼𝘂𝗽")
    desc = "\n".join(parts)
    label = "𝗯𝗼𝘁𝗵" if len(missing) > 1 else "𝗴𝗿𝗼𝘂𝗽" if "group" in missing else "𝗰𝗵𝗮𝗻𝗻𝗲𝗹"
    text = (
        "𝗔𝗰𝗰𝗲𝘀𝘀 𝗕𝗹𝗼𝗰𝗸𝗲𝗱\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{desc}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"╰ 𝗝𝗼𝗶𝗻 {label} 𝗮𝗻𝗱 𝘁𝗮𝗽 𝘃𝗲𝗿𝗶𝗳𝘆"
    )
    kb = []
    row = []
    if "channel" in missing:
        row.append(Button.url("𝗖𝗵𝗮𝗻𝗻𝗲𝗹", "https://t.me/GODFATHERCHECKER"))
    if "group" in missing:
        row.append(Button.url("𝗚𝗿𝗼𝘂𝗽", config.REQUIRED_GROUP))
    if row:
        kb.append(row)
    kb.append([Button.inline("𝗩𝗲𝗿𝗶𝗳𝘆", "verify_join", style='success')])
    try:
        await client.send_file(event.chat_id, config.PHOTO_PATH, caption=text, buttons=kb, parse_mode='html')
    except:
        await client.send_message(event.chat_id, text, buttons=kb, parse_mode='html')
    return False
