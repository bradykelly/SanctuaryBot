from discord import utils

# If Solaris can't use the correct emojis, fall back to these.
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


class EmojiGetter:
    def __init__(self, bot):
        self.bot = bot

    def get(self, name):
        hub = self.bot.get_cog("Hub")

        if getattr(hub, "guild", None) is not None:
            return utils.get(hub.guild.emojis, name=name) or ALTERNATIVES[name]
        else:
            return ALTERNATIVES[name]

    def mention(self, name):
        hub = self.bot.get_cog("Hub")

        if getattr(hub, "guild", None) is not None:
            return f"{utils.get(hub.guild.emojis, name=name) or ALTERNATIVES[name] or ''}"
        else:
            return ALTERNATIVES[name] or ""
