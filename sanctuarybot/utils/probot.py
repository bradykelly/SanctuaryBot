import discord
from discord.ext import commands
from discord.channel import TextChannel

HARD_PROBOT_NAME = 'ProBot'
HARD_READ_CHANNEL_NAME = "probot"
HARD_MESSAGE_COUNT = 15

class ProBotConfig():
#TODO Error handling for db calls
    def __init__(self, bot): 
        self.bot = bot

    async def get_read_channel(self, ctx): 
        channel_name = self.bot.db.field("SELECT read_channel_name FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        if channel_name is not None:
            channel_name = channel_name.lower()
        return discord.utils.get(ctx.guild.channels, name=channel_name or HARD_READ_CHANNEL_NAME)

    async def get_read_count(self, ctx):
        msg_count = self.bot.db.field("SELECT read_message_count FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        return msg_count or HARD_MESSAGE_COUNT

    async def get_probot_member(self, ctx):
        bot_name = self.bot.db.field("SELECT probot_name FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        for member in ctx.guild.members:
            if member.display_name == bot_name or HARD_PROBOT_NAME:
                return member
        return None


