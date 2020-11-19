from os import getenv
from typing import Final
from dotenv import load_dotenv

load_dotenv()

MAX_PREFIX_LEN = 5
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
MAX_GATETEXT_LEN = 250
MAX_WGTEXT_LEN = 1000
MAX_WGBOTTEXT_LEN = 500

class Config:
    try:
        # Load production token.
        with open(getenv("TOKEN", "")) as f:
            token = f.read()
    except FileNotFoundError:
        # Load development token.
        token = getenv("TOKEN", "")

    TOKEN: Final = token
    DEFAULT_PREFIX: Final = getenv("DEFAULT_PREFIX", "->")
    BOT_NAME: Final = getenv("BOT_NAME", "SanctuaryBot")