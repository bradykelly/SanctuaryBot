import discord
from discord.ext import commands
from sanctuarybot.utils.output import OutputUtils


class BaseCog(commands.Cog):
    """Base class for application cogs in this bot"""

    def __init__(self):
        self.output = OutputUtils()
