from os import getenv
from typing import Final
from dotenv import load_dotenv

load_dotenv()

BOT_VERSION = "0.1.0"
CSV_SEPARATOR = ";"
DEFAULT_NOTEBOOK = "Main"
MENU_TIMEOUT2 = 1200.0
MENU_TIMEOUT5 = 300.0

MAX_PREFIX_LEN = 5
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
MAX_GATETEXT_LEN = 250
MAX_WGTEXT_LEN = 1000
MAX_WGBOTTEXT_LEN = 500

class Config:
    try:
        with open(getenv("TOKEN", "")) as f:
            token = f.read()
    except FileNotFoundError:
        token = getenv("TOKEN", "")

    try:
        with open(getenv("DSN", "")) as f:
            dsn = f.read()
    except  FileNotFoundError:
        dsn = getenv("DSN", "")

    TOKEN: Final = token
    DSN: Final = dsn
    HARD_DEFAULT_PREFIX: Final = "@!"
    DEFAULT_PREFIX: Final = getenv("DEFAULT_PREFIX", HARD_DEFAULT_PREFIX)    
    BOT_NAME: Final = getenv("BOT_NAME", "SanctuaryBot")
    HUB_GUILD_ID: Final = int(getenv("HUB_GUILD_ID", ""))
    HUB_COMMANDS_CHANNEL_ID: Final = int(getenv("HUB_COMMANDS_CHANNEL_ID", ""))
    HUB_RELAY_CHANNEL_ID: Final = int(getenv("HUB_RELAY_CHANNEL_ID", ""))
    HUB_STDOUT_CHANNEL_ID: Final = int(getenv("HUB_STDOUT_CHANNEL_ID", ""))