import discord
from discord.ext import commands


class BaseCog(commands.Cog):
    """Base class for application cogs in this bot"""

    def __init__(self, bot):
        self.bot = bot

