ADMIN_ID = "ADMIN_ID"
BOT_TOKEN = "BOT_TOKEN"
DEBUG_MODE = "DEBUG_MODE"

ACTIVITIES = [
    "малорухливий",
    "легка активність",
    "помірно активний",
    "дуже активний",
    "надзвичайно активний",
]
CLIMATES = ["тропічний", "помірний", "холодний"]

ACTIVITY_MAP = {
    "малорухливий": 1.0,
    "легка активність": 1.1,
    "помірно активний": 1.2,
    "дуже активний": 1.3,
    "надзвичайно активний": 1.4,
}

CLIMATE_MAP = {
    "тропічний": 1.7,
    "помірний": 1.1,
    "холодний": 0.9,
}

HOUR = 3600
MINUTE = 60
NOON = 12

NOTIFY_THRESHOLD = HOUR * 2
NOTIFY_FREQUENCY_MIN = 5
NOTIFY_FREQUENCY_MAX = 60

DEFAULT_TZ = "Europe/Kiev"
