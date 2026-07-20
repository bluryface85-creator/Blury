from telethon import Button, events

def main_menu():
    return [
        [Button.inline("𝗚𝗮𝘁𝗲𝘀", "menu_gates", style='success'),
         Button.inline("𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀", "menu_commands", style='success')],
        [Button.inline("𝗣𝗿𝗼𝗳𝗶𝗹𝗲", "menu_profile", style='success'),
         Button.inline("𝗣𝗿𝗶𝗰𝗶𝗻𝗴", "menu_pricing", style='success')],
        [Button.inline("𝗖𝗹𝗼𝘀𝗲", "menu_close", style='danger')],
    ]

def commands_menu(uid=None):
    import utils
    btns = [
        [Button.inline("𝗧𝗼𝗼𝗹𝘀", "cmd_tools", style='success'),
         Button.inline("𝗣𝗿𝗼𝘅𝘆", "cmd_proxy", style='success')],
    ]
    if uid and utils.is_admin(uid):
        btns[0].append(Button.inline("𝗔𝗱𝗺𝗶𝗻", "cmd_admin", style='success'))
    btns.append([Button.inline("𝗕𝗮𝗰𝗸", "menu_back", style='danger')])
    return btns

def back_btn():
    return [[Button.inline("𝗕𝗮𝗰𝗸", "menu_back", style='danger')]]

def cmd_back_btn():
    return [[Button.inline("𝗕𝗮𝗰𝗸", "cmd_back", style='danger')]]

def gate_back_btn():
    return [[Button.inline("𝗕𝗮𝗰𝗸", "gates_back", style='danger')]]

def gates_menu():
    return [
        [Button.inline("𝗖𝗵𝗮𝗿𝗴𝗲", "gates_charge", style='success'),
         Button.inline("𝗔𝘂𝘁𝗵", "gates_auth", style='success')],
        [Button.inline("𝗕𝗮𝗰𝗸", "menu_back", style='danger')],
    ]

TEXTS = {
    "welcome": "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗣𝘂𝘀𝘀𝘆 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 🕊️\n━━━━━━━━━━━━━━━━━\n𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻 𝗯𝗲𝗹𝗼𝘄",
    "gates": "𝗚𝗮𝘁𝗲𝘀\n━━━━━━━━━━━━━━━━━━━━\n𝟭. 𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮\n╰ /sh    𝗦𝗶𝗻𝗴𝗹𝗲 𝗖𝗵𝗲𝗰𝗸\n╰ /msh   𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸\n\n𝟮. 𝙎𝙩𝙧𝙞𝙥𝙚 𝘼𝙪𝙩𝙝\n╰ 𝗢𝗙𝗙",

    # populated dynamically

    "tools": "⋆ 𝗧𝗼𝗼𝗹𝘀\n━━━━━━━━━━━━━━━━━\n▸ /bin  ━ 𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽\n▸ /gen  ━ 𝗖𝗮𝗿𝗱 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿\n▸ /fake  ━ 𝗙𝗮𝗸𝗲 𝗜𝗻𝗳𝗼\n▸ /redeem  ━ 𝗥𝗲𝗱𝗲𝗲𝗺 𝗞𝗲𝘆",
    "proxy": "⋆ 𝗣𝗿𝗼𝘅𝘆\n━━━━━━━━━━━━━━━━━\n▸ /proxy add  ━ 𝗔𝗱𝗱 𝗣𝗿𝗼𝘅𝘆\n▸ /proxy list  ━ 𝗟𝗶𝘀𝘁 𝗣𝗿𝗼𝘅𝗶𝗲𝘀\n▸ /proxy test  ━ 𝗧𝗲𝘀𝘁 𝗣𝗿𝗼𝘅𝗶𝗲𝘀\n▸ /proxy remove  ━ 𝗥𝗲𝗺𝗼𝘃𝗲 𝗣𝗿𝗼𝘅𝘆",
    "commands_header": "⋆ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀\n━━━━━━━━━━━━━━━━━\n𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗰𝗮𝘁𝗲𝗴𝗼𝗿𝘆",
    "pricing": "𝗟𝗜𝗧𝗘 𝗣𝗟𝗔𝗡\n✗ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 ↬ 7 days\n✗ 𝗣𝗿𝗶𝗰𝗲 ↬ 6$\n━━━━━━━━━━━━━━━━━━\n𝗕𝗔𝗦𝗜𝗖 𝗣𝗟𝗔𝗡\n✗ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 ↬ 15 days\n✗ 𝗣𝗿𝗶𝗰𝗲 ↬ 13$\n━━━━━━━━━━━━━━━━━━\n𝗫 𝗣𝗟𝗔𝗡\n✗ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 ↬ 30 days\n✗ 𝗣𝗿𝗶𝗰𝗲 ↬ 25$\n━━━━━━━━━━━━━━━━━━\n𝗥𝗜𝗣 𝗣𝗟𝗔𝗡\n✗ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 ↬ 90 days\n✗ 𝗣𝗿𝗶𝗰𝗲 ↬ 25$\n━━━━━━━━━━━━━━━━━━\n𝗧𝗼 𝗣𝘂𝗿𝗰𝗵𝗮𝘀𝗲: 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿",
    "admin": "⋆ 𝗔𝗱𝗺𝗶𝗻\n━━━━━━━━━━━━━━━━━\n▸ /ban  ━ 𝗕𝗮𝗻 𝗨𝘀𝗲𝗿\n▸ /unban  ━ 𝗨𝗻𝗯𝗮𝗻 𝗨𝘀𝗲𝗿\n▸ /addplan  ━ 𝗔𝗱𝗱 𝗣𝗹𝗮𝗻\n▸ /rmplan  ━ 𝗥𝗲𝗺𝗼𝘃𝗲 𝗣𝗹𝗮𝗻\n▸ /stats  ━ 𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝘀\n▸ /gkey  ━ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗞𝗲𝘆𝘀\n▸ /keylist  ━ 𝗟𝗶𝘀𝘁 𝗨𝗻𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱\n▸ /rkey  ━ 𝗥𝗲𝘃𝗼𝗸𝗲 𝗞𝗲𝘆\n▸ /maintenance  ━ 𝗢𝗻/𝗢𝗳𝗳\n▸ /broadcast  ━ 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁\n▸ /addadmin  ━ 𝗔𝗱𝗱 𝗔𝗱𝗺𝗶𝗻\n▸ /rmadmin  ━ 𝗥𝗲𝗺𝗼𝘃𝗲 𝗔𝗱𝗺𝗶𝗻\n▸ /auth  ━ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗖𝘂𝘀𝘁𝗼𝗺 𝗞𝗲𝘆",
}

def register(client):
    import utils, database as db, time, config

    @client.on(events.NewMessage(pattern=r'^/start(\s|$|@)'))
    async def start_handler(event):
        if not utils.is_authorized(event):
            return
        if not await utils.require_membership(client, event):
            return
        text = utils.premium_emoji(TEXTS["welcome"])
        try:
            await client.send_file(event.chat_id, config.PHOTO_PATH, caption=text,
                                   buttons=main_menu(), parse_mode='html')
        except:
            await client.send_message(event.chat_id, text,
                                      buttons=main_menu(), parse_mode='html')

    @client.on(events.CallbackQuery)
    async def menu_callback(event):
        data = event.data.decode()
        if not (data.startswith("menu_") or data.startswith("cmd_") or data.startswith("gates_")):
            return
        uid = event.sender_id

        if data == "menu_gates":
            await event.edit(
                f"𝗚𝗮𝘁𝗲𝘀\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 𝗧𝗼𝘁𝗮𝗹 𝗚𝗮𝘁𝗲𝘀: 2\n"
                f"┣ 𝗖𝗵𝗮𝗿𝗴𝗲: 1\n"
                f"┣ 𝗔𝘂𝘁𝗵: 1\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┗ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗴𝗮𝘁𝗲",
                buttons=gates_menu())

        elif data == "menu_commands":
            is_adm = utils.is_admin(uid)
            tools_count = 4
            proxy_count = 4
            admin_count = 13 if is_adm else 0
            total_cmd = tools_count + proxy_count + admin_count
            text = (
                f"𝗖𝗼𝗺𝗺ᴀɴᴅ𝘀\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 𝗧ᴏᴛᴀʟ 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {total_cmd}\n"
                f"┣ 𝗧ᴏᴏʟ𝘀 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {tools_count}\n"
                f"┣ 𝗣ʀᴏxʏ 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {proxy_count}\n"
            )
            if is_adm:
                text += f"┣ 𝗔ᴅᴍɪɴ 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {admin_count}\n"
            text += f"━━━━━━━━━━━━━━━━━━━━\n┗ 𝗦ᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ"
            await client.edit_message(event.chat_id, event.message_id, text,
                                      buttons=commands_menu(uid))

        elif data == "menu_profile":
            name = event.sender.first_name or "N/A"
            uname = f"@{event.sender.username}" if event.sender.username else "N/A"

            from Commands.Admin.plan import get_user_plan
            _, plan_display, expiry_str, limit = get_user_plan(uid)
            rank = f"[{plan_display}]"
            if utils.is_admin(uid):
                limit = "5000"
                expiry = "𝗟𝗜𝗙𝗘𝗧𝗜𝗠𝗘"
            elif db.is_premium(uid):
                expiry = expiry_str
            else:
                expiry = "𝗡𝗼𝗻𝗲"

            profile_text = (
                f"⋆ 𝗣𝗿𝗼𝗳𝗶𝗹𝗲\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"▸ 𝗜𝗗: {uid}\n"
                f"▸ 𝗡𝗮𝗺𝗲: {name}\n"
                f"▸ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: {uname}\n"
                f"▸ 𝗣𝗹𝗮𝗻: {rank}\n"
                f"▸ 𝗘𝘅𝗽𝗶𝗿𝘆: {expiry}\n"
                f"▸ 𝗟𝗶𝗺𝗶𝘁: {limit}\n"
                f"━━━━━━━━━━━━━━━━━"
            )
            await client.edit_message(event.chat_id, event.message_id, profile_text, buttons=back_btn())

        elif data == "gates_charge":
            await client.edit_message(event.chat_id, event.message_id,
                "𝗖𝗵𝗮𝗿𝗴𝗲\n━━━━━━━━━━━━━━━━━━━━\n𝟭. 𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮\n╰ /sh    𝗦𝗶𝗻𝗴𝗹𝗲 𝗖𝗵𝗲𝗰𝗸\n╰ /msh   𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸", buttons=gate_back_btn())

        elif data == "gates_auth":
            await client.edit_message(event.chat_id, event.message_id,
                "𝗔𝘂𝘁𝗵\n━━━━━━━━━━━━━━━━━━━━\n\n𝟭. 𝙎𝙩𝙧𝙞𝙥𝙚 𝘼𝙪𝙩𝙝\n╰ /sa     𝗦𝗶𝗻𝗴𝗹𝗲 𝗖𝗵𝗲𝗰𝗸\n╰ /msa    𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸", buttons=gate_back_btn())

        elif data == "gates_back":
            await client.edit_message(event.chat_id, event.message_id,
                f"𝗚𝗮𝘁𝗲𝘀\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 𝗧𝗼𝘁𝗮𝗹 𝗚𝗮𝘁𝗲𝘀: 2\n"
                f"┣ 𝗖𝗵𝗮𝗿𝗴𝗲: 1\n"
                f"┣ 𝗔𝘂𝘁𝗵: 1\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┗ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗴𝗮𝘁𝗲",
                buttons=gates_menu())

        elif data == "menu_pricing":
            await client.edit_message(event.chat_id, event.message_id, TEXTS["pricing"], buttons=back_btn())

        elif data in ("cmd_tools", "cmd_proxy", "cmd_admin"):
            key = data.split("_")[1]
            if key == "admin" and not utils.is_admin(uid):
                await event.answer("𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱", alert=True)
                return
            await client.edit_message(event.chat_id, event.message_id, TEXTS[key], buttons=cmd_back_btn())

        elif data == "cmd_back":
            is_adm = utils.is_admin(uid)
            tools_count = 4
            proxy_count = 4
            admin_count = 13 if is_adm else 0
            total_cmd = tools_count + proxy_count + admin_count
            text = (
                f"𝗖𝗼𝗺𝗺ᴀɴᴅ𝘀\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 𝗧ᴏᴛᴀʟ 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {total_cmd}\n"
                f"┣ 𝗧ᴏᴏʟ𝘀 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {tools_count}\n"
                f"┣ 𝗣ʀᴏxʏ 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {proxy_count}\n"
            )
            if is_adm:
                text += f"┣ 𝗔ᴅᴍɪɴ 𝗖ᴏᴍᴍᴀɴᴅ𝘀: {admin_count}\n"
            text += f"━━━━━━━━━━━━━━━━━━━━\n┗ 𝗦ᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ"
            await client.edit_message(event.chat_id, event.message_id, text,
                                      buttons=commands_menu(uid))

        elif data == "menu_back":
            text = utils.premium_emoji(TEXTS["welcome"])
            await client.edit_message(event.chat_id, event.message_id, text,
                                      buttons=main_menu(), parse_mode='html')

        elif data == "menu_close":
            await client.delete_messages(event.chat_id, [event.message_id])

        await event.answer()

    @client.on(events.CallbackQuery(data=b'verify_join'))
    async def verify_callback(event):
        uid = event.sender_id
        await event.answer()
        missing = await utils.check_membership(client, uid)
        if missing:
            parts = []
            if "channel" in missing:
                parts.append("╰ 𝗖𝗵𝗮𝗻𝗻𝗲𝗹")
            if "group" in missing:
                parts.append("╰ 𝗚𝗿𝗼𝘂𝗽")
            desc = "\n".join(parts)
            text = (
                "𝗔𝗰𝗰𝗲𝘀𝘀 𝗕𝗹𝗼𝗰𝗸𝗲𝗱\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{desc}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"╰ 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲𝗻'𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝘆𝗲𝘁"
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
                await event.edit(text, buttons=kb, parse_mode='html')
            except:
                pass
        else:
            text = utils.premium_emoji(TEXTS["welcome"])
            try:
                await event.edit(text, buttons=main_menu(), parse_mode='html')
            except:
                pass
