from decouple import config

TELEGRAM_TOKEN = config("TELEGRAM_TOKEN", None)
VK_TOKEN = config("VK_TOKEN", None)
REDIS_URL = config("REDIS_URL", default=None)
WS_URL = "wss://api.aidungeon.io/subscriptions"

YANDEX_FOLDER_ID = config("YANDEX_FOLDER_ID")
YANDEX_IAM_TOKEN = config("YANDEX_IAM_TOKEN")
