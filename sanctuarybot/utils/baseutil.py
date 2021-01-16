from sanctuarybot.utils.output import OutputUtils


class BaseUtil():
    """Base class for utility classes in this bot"""

    def __init__(self, bot):
        self.bot = bot
        self.output = OutputUtils()