import asyncio, sys, os, threading, time
from telethon import TelegramClient
import config
from Commands.Admin import register as register_admin
from Commands.Admin.maintenance import register as register_maintenance
from Commands.User.Buttons import register as register_buttons
from Commands.User.Tools import register as register_tools
from Commands.User.Proxy import register as register_proxy
from Commands.User.Gates import register as register_gates
from Commands.User.redeem import register as register_redeem

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

client = TelegramClient('bot_session', config.API_ID, config.API_HASH)

from utils import check_expired_premiums

async def run_api():
    import sys as _sys
    null = open(os.devnull, 'w')
    save_out, save_err = _sys.stdout, _sys.stderr
    _sys.stdout, _sys.stderr = null, null
    try:
        from Api.api import app
        import uvicorn
        config = uvicorn.Config(app, host='0.0.0.0', port=5000, log_level='critical')
        server = uvicorn.Server(config)
        await server.serve()
    finally:
        _sys.stdout, _sys.stderr = save_out, save_err
        null.close()

async def main():
    await client.start(bot_token=config.BOT_TOKEN)
    print("𝗕𝗢𝗧 𝗜𝗦 𝗥𝗨𝗡𝗡𝗜𝗡𝗚...")

    register_maintenance(client)
    register_admin(client)
    register_buttons(client)
    register_tools(client)
    register_proxy(client)
    register_gates(client)
    register_redeem(client)

    threading.Thread(target=asyncio.run, args=(check_expired_premiums(client),), daemon=True).start()
    threading.Thread(target=asyncio.run, args=(run_api(),), daemon=True).start()

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
