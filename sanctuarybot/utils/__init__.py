# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/__init__.py
from json import load
from pathlib import Path

DEFAULT_EMBED_COLOUR = 0xE99234

# Dependant on constants above.
from .embed import EmbedConstructor
from .emoji import EmojiGetter
