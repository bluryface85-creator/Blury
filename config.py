DATA_DIR = "Data"

BOT_TOKEN = "8812563837:AAEYIAamFfWX6UoWwfIntG0C6-ckap6SXy4"
ADMIN_IDS = [7221087191, 8606381959]
API_HASH = "4f3cf0c0102701397629560c7a12d3a0"
API_ID = 24653878
AUTHORIZED_GROUP = -1003885954549
LOGS_GROUP = -1003885954549
PHOTO_PATH = "rip.jpg"
REQUIRED_CHANNEL = "@GODFATHERCHECKER"
REQUIRED_GROUP = "https://t.me/godfatherchats"
REQUIRED_CHANNEL_ID = -1003946680511
REQUIRED_GROUP_ID = -1003832544458

WORKERS = 25
RETRY_ON_ERRORS = 3

PROXY_LIMIT = 30

LITE_CC_LIMIT = 500
BASIC_CC_LIMIT = 1000
X_CC_LIMIT = 2000
RIP_CC_LIMIT = 5000

PREMIUM_EMOJI_IDS = {
    "🕊️": "4904862405902730286",
    "💎": "6221753169026749958",
    "✅": "5980797575211520457",
    "❌": "6100670215522094562",
    "🔥": "5116414868357907335",
    "🐆": "5172843385643336752",
    "⚠️": "5904692292324692386",
    "💫": "5134202243486057363",
    "🐋": "5134201302888219205",
    "❎": "5348235470461483629",
    "⭕️": "5122933683820430249",
    "👻": "5082478549340783285",
    "💳": "5447453226498552490",
    "▶️": "5447181973544008180",
    "⚡️": "5348235470461483629",
}

ERROR_KEYWORDS = [
    'receipt id is empty', 'handle is empty', 'product id is empty',
    'tax amount is empty', 'payment method identifier is empty',
    'invalid url', 'error in 1st req', 'error in 1 req',
    'cloudflare', 'connection failed', 'timed out',
    'access denied', 'tlsv1 alert', 'ssl routines',
    'could not resolve', 'domain name not found',
    'name or service not known', 'openssl ssl_connect',
    'empty reply from server', 'httperror504', 'http error',
    'timeout', 'unreachable', 'ssl error',
    '502', '503', '504', 'bad gateway', 'service unavailable',
    'gateway timeout', 'network error', 'connection reset',
    'failed to detect product',     'failed to create checkout',
    'proxy error', 'cannot connect to host',
    'failed to tokenize card', 'failed to get proposal data',
    'submit rejected', 'submit rejected:', 'handle error', 'http 404',
    'delivery_delivery_line_detail_changed', 'delivery_address2_required',
    'url rejected', 'malformed input', 'amount_too_small', 'amount too small',
    'site dead', 'captcha_required', 'captcha required', 'site errors', 'failed',
    'all products sold out', 'no_session_token', 'tokenize_fail', 'generic_error', 'generic error',
    'ERROR', 'GENERIC_ERROR', 'PAYMENTS_CREDIT_CARD_GENERIC',
    'DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE_FOR_MERCHANDISE_LINE',
    'NO_VARIANTS', 'RATE_LIMITED',
    'MERCHANDISE_PRODUCT_NOT_PUBLISHED_IN_BUYER_LOCATION',
    'MERCHANDISE_OUT_OF_STOCK', 'FAILD_TO_ADD_TO_CART', 'WAITING_PENDING_TERMS',
    'Cart failed with status 429', 'Site Error! Status: 402',
    'Site not supported',
]
