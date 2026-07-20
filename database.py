import sqlite3, json, time, os, threading

DB_FILE = "database.db"
DATA_DIR = "Data"
_local = threading.local()

os.makedirs(DATA_DIR, exist_ok=True)

for f in ["premium.txt", "users.txt", "banned.txt", "proxies.txt"]:
    path = os.path.join(DATA_DIR, f)
    if not os.path.exists(path):
        open(path, "w").close()

def get_conn():
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=DELETE")
    return _local.conn

def _sync_file(table, filepath, serializer):
    """Sync SQLite table to text file."""
    try:
        conn = get_conn()
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        with open(filepath, "w") as f:
            for row in rows:
                f.write(serializer(row) + "\n")
    except:
        pass

def _append_file(filepath, line):
    try:
        with open(filepath, "a") as f:
            f.write(line + "\n")
    except:
        pass

def init():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_seen REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS premium (
            user_id INTEGER PRIMARY KEY,
            expiry REAL NOT NULL DEFAULT 0,
            plan TEXT NOT NULL DEFAULT 'PREMIUM'
        );
        CREATE TABLE IF NOT EXISTS banned (
            user_id INTEGER PRIMARY KEY,
            expiry REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proxy TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS approved_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card TEXT NOT NULL,
            response TEXT,
            timestamp REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS threeds_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card TEXT NOT NULL,
            response TEXT,
            timestamp REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            plan TEXT NOT NULL,
            used_by INTEGER DEFAULT NULL,
            redeemed_at REAL DEFAULT NULL,
            created_at REAL NOT NULL,
            revoked INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, key)
        );
    """)
    try:
        conn.execute("ALTER TABLE premium ADD COLUMN plan TEXT NOT NULL DEFAULT 'PREMIUM'")
    except:
        pass
    try:
        conn.execute("ALTER TABLE keys ADD COLUMN days INTEGER DEFAULT NULL")
    except:
        pass
    try:
        conn.execute("ALTER TABLE keys ADD COLUMN revoked INTEGER NOT NULL DEFAULT 0")
    except:
        pass
    conn.commit()

def add_user(user_id):
    conn = get_conn()
    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()[0] > 0
    conn.execute("INSERT OR IGNORE INTO users (user_id, first_seen) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    if not exists:
        _append_file(os.path.join(DATA_DIR, "users.txt"), str(user_id))

def is_premium(user_id):
    row = get_conn().execute("SELECT expiry FROM premium WHERE user_id = ?", (user_id,)).fetchone()
    if row:
        exp = row["expiry"]
        return exp == 0 or time.time() < exp
    return False

def get_premium_plan(user_id):
    row = get_conn().execute("SELECT plan FROM premium WHERE user_id = ?", (user_id,)).fetchone()
    return row["plan"] if row else None

def add_premium(user_id, expiry, plan='PREMIUM'):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO premium (user_id, expiry, plan) VALUES (?, ?, ?)", (user_id, expiry, plan))
    conn.commit()
    _sync_file("premium", os.path.join(DATA_DIR, "premium.txt"),
               lambda r: f"{r['user_id']}|{r['expiry']}|{r['plan']}")

def remove_premium(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM premium WHERE user_id = ?", (user_id,))
    conn.commit()
    _sync_file("premium", os.path.join(DATA_DIR, "premium.txt"),
               lambda r: f"{r['user_id']}|{r['expiry']}")

def get_premium_count():
    return get_conn().execute("SELECT COUNT(*) FROM premium").fetchone()[0]

def is_banned(user_id):
    row = get_conn().execute("SELECT expiry FROM banned WHERE user_id = ?", (user_id,)).fetchone()
    if row:
        exp = row["expiry"]
        return exp == 0 or time.time() < exp
    return False

def add_ban(user_id, expiry):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO banned (user_id, expiry) VALUES (?, ?)", (user_id, expiry))
    conn.commit()
    _sync_file("banned", os.path.join(DATA_DIR, "banned.txt"),
               lambda r: f"{r['user_id']}|{r['expiry']}")

def remove_ban(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM banned WHERE user_id = ?", (user_id,))
    conn.commit()
    _sync_file("banned", os.path.join(DATA_DIR, "banned.txt"),
               lambda r: f"{r['user_id']}|{r['expiry']}")

def get_banned_count():
    return get_conn().execute("SELECT COUNT(*) FROM banned").fetchone()[0]

def get_total_users():
    row = get_conn().execute("SELECT COUNT(*) FROM users").fetchone()
    return row[0] if row else 0

def get_all_user_ids():
    rows = get_conn().execute("SELECT user_id FROM users").fetchall()
    return [r["user_id"] for r in rows]

def get_stat(key):
    row = get_conn().execute("SELECT value FROM stats WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else 0

def incr_stat(key):
    conn = get_conn()
    conn.execute("INSERT INTO stats (key, value) VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1", (key,))
    conn.commit()
    _sync_stats_file()

def get_all_stats():
    rows = get_conn().execute("SELECT key, value FROM stats").fetchall()
    return {r["key"]: r["value"] for r in rows}

def save_stats(stats_dict):
    conn = get_conn()
    for k, v in stats_dict.items():
        conn.execute("INSERT OR REPLACE INTO stats (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    _sync_stats_file()

def _sync_stats_file():
    try:
        rows = get_conn().execute("SELECT key, value FROM stats").fetchall()
        with open(os.path.join(DATA_DIR, "stats.json"), "w") as f:
            json.dump({r["key"]: r["value"] for r in rows}, f)
    except:
        pass

def add_approved(card, response):
    conn = get_conn()
    conn.execute("INSERT INTO approved_cards (card, response, timestamp) VALUES (?, ?, ?)",
                 (card, response, time.time()))
    conn.commit()
    incr_stat("approved")

def add_3ds(card, response):
    conn = get_conn()
    conn.execute("INSERT INTO threeds_cards (card, response, timestamp) VALUES (?, ?, ?)",
                 (card, response, time.time()))
    conn.commit()
    incr_stat("3ds")

def get_all_proxies():
    rows = get_conn().execute("SELECT id, proxy FROM proxies ORDER BY id").fetchall()
    return [r["proxy"] for r in rows]

def add_proxy(proxy):
    try:
        get_conn().execute("INSERT INTO proxies (proxy) VALUES (?)", (proxy,))
        get_conn().commit()
        _sync_file("proxies", os.path.join(DATA_DIR, "proxies.txt"), lambda r: r["proxy"])
        return True
    except sqlite3.IntegrityError:
        return False

def remove_proxy_by_id(pid):
    get_conn().execute("DELETE FROM proxies WHERE id = ?", (pid,))
    get_conn().commit()
    _sync_file("proxies", os.path.join(DATA_DIR, "proxies.txt"), lambda r: r["proxy"])

def remove_all_proxies():
    get_conn().execute("DELETE FROM proxies")
    get_conn().commit()
    open(os.path.join(DATA_DIR, "proxies.txt"), "w").close()

def get_expired_premiums():
    now = time.time()
    rows = get_conn().execute("SELECT user_id FROM premium WHERE expiry > 0 AND expiry < ?", (now,)).fetchall()
    return [r["user_id"] for r in rows]

def get_expired_bans():
    now = time.time()
    rows = get_conn().execute("SELECT user_id FROM banned WHERE expiry > 0 AND expiry < ?", (now,)).fetchall()
    return [r["user_id"] for r in rows]

def add_key(key, plan, days=None):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO keys (key, plan, days, created_at) VALUES (?, ?, ?, ?)", (key, plan, days, time.time()))
        conn.commit()
        return True
    except:
        return False

def get_key(key):
    return get_conn().execute("SELECT * FROM keys WHERE key = ?", (key,)).fetchone()

def redeem_key(key, user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM keys WHERE key = ?", (key,)).fetchone()
    if not row:
        return "invalid"
    if row["revoked"]:
        return "revoked"
    if row["used_by"] is not None:
        return "used"
    conn.execute("UPDATE keys SET used_by = ?, redeemed_at = ? WHERE key = ?", (user_id, time.time(), key))
    conn.commit()
    try:
        days = row["days"]
    except (IndexError, KeyError):
        days = None
    return (row["plan"], days)

def revoke_key(key):
    conn = get_conn()
    row = conn.execute("SELECT * FROM keys WHERE key = ?", (key,)).fetchone()
    if not row:
        return False
    conn.execute("UPDATE keys SET revoked = 1 WHERE key = ?", (key,))
    conn.commit()
    return True

def revoke_all_keys():
    conn = get_conn()
    conn.execute("UPDATE keys SET revoked = 1 WHERE revoked = 0")
    conn.commit()

def get_unredeemed_keys():
    return get_conn().execute("SELECT * FROM keys WHERE used_by IS NULL AND revoked = 0 ORDER BY plan, created_at").fetchall()

def incr_user_stat(user_id, key, amount=1):
    conn = get_conn()
    conn.execute("INSERT INTO user_stats (user_id, key, value) VALUES (?, ?, ?) ON CONFLICT(user_id, key) DO UPDATE SET value = value + ?",
                 (user_id, key, amount, amount))
    conn.commit()

def get_user_stat(user_id, key):
    row = get_conn().execute("SELECT value FROM user_stats WHERE user_id = ? AND key = ?", (user_id, key)).fetchone()
    return row["value"] if row else 0

def get_top_users(key, limit=10):
    rows = get_conn().execute(
        "SELECT user_id, value FROM user_stats WHERE key = ? ORDER BY value DESC LIMIT ?",
        (key, limit)
    ).fetchall()
    return [(r["user_id"], r["value"]) for r in rows]

init()
