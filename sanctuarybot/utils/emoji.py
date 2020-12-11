# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/__init__.py

from discord import utils


# If SanctuaryBot can't use the correct emojis, fall back to these.
ALTERNATIVES = {
    "confirm": "✅",
    "cancel": "❎",
    "exit": "⏏️",
    "info": "ℹ️",
    "loading": "⏱️",
    "option1": "1️⃣",
    "option2": "2⃣",
    "option3": "3⃣",
    "option4": "4⃣",
    "option5": "5⃣",
    "option6": "6⃣",
    "option7": "7⃣",
    "option8": "8⃣",
    "option9": "9⃣",
    "pageback": "◀️",
    "pagenext": "▶️",
    "stepback": "⏪",
    "stepnext": "⏩",
}

class EmojiUtils:
    def __init__(self, bot):
        self.bot = bot

    def get(self, guild, name):
        emoji = utils.get(guild.emojis, name=name) or ALTERNATIVES[name]
        return emoji

    def mention(self, guild, name):
        return f"{utils.get(guild.emojis, name=name) or ALTERNATIVES[name] or ''}"
