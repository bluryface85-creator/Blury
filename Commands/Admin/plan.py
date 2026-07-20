import time
import database as db
import config

PLANS = {
    "admin": {"display": "𝗔𝗗𝗠𝗜𝗡", "cc_limit": 999999, "proxy_limit": config.PROXY_LIMIT},
    "lite": {"display": "𝗟𝗜𝗧𝗘", "cc_limit": config.LITE_CC_LIMIT, "proxy_limit": config.PROXY_LIMIT},
    "basic": {"display": "𝗕𝗔𝗦𝗜𝗖", "cc_limit": config.BASIC_CC_LIMIT, "proxy_limit": config.PROXY_LIMIT},
    "x": {"display": "𝗫", "cc_limit": config.X_CC_LIMIT, "proxy_limit": config.PROXY_LIMIT},
    "rip": {"display": "𝗥𝗜𝗣", "cc_limit": config.RIP_CC_LIMIT, "proxy_limit": config.PROXY_LIMIT},
    "free": {"display": "𝗨𝗦𝗘𝗥", "cc_limit": 0, "proxy_limit": 0},
}

def _bold_plan(plan):
    import utils
    return utils.sbold(plan)

def get_user_plan(user_id):
    if user_id in config.ADMIN_IDS:
        return "admin", "𝗔𝗗𝗠𝗜𝗡", "𝗟𝗜𝗙𝗘𝗧𝗜𝗠𝗘", 999999
    if db.is_premium(user_id):
        row = db.get_conn().execute("SELECT expiry, plan FROM premium WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            exp = row["expiry"]
            plan_name = row["plan"].lower()
            bplan = _bold_plan(plan_name)
            cc_limit = PLANS.get(plan_name, PLANS["free"])["cc_limit"]
            if exp == 0:
                return plan_name, bplan, "𝗟𝗜𝗙𝗘𝗧𝗜𝗠𝗘", cc_limit
            elif time.time() < exp:
                exp_str = time.strftime("%Y-%m-%d", time.localtime(exp))
                return plan_name, bplan, exp_str, cc_limit
    return "free", "𝗨𝗦𝗘𝗥", "𝗡𝗼𝗻𝗲", 0
