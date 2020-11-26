import discord
from sanctuarybot.exceptions import ConfigError

#TODO Document that admin should assign the nick 'Probot' to Probot to avoid uglies with special chars
HARD_PROBOT_NAME = 'ProBot ✨'
HARD_READ_CHANNEL_NAME = "probot"
HARD_MESSAGE_COUNT = 50

class ProBotUtils():
    """Functions for reading and parsing messages from the ProBot bot"""

    def __init__(self, bot): 
        self.bot = bot
        #self.error = self.bot.get_cog("Error")

    async def get_read_channel(self, ctx): 
        try:
            error = self.bot.get_cog("Error")
            channel_name = await self.bot.db.field("SELECT read_channel_name FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            self.error.log_error(exc)
            return HARD_READ_CHANNEL_NAME
        if channel_name is not None:
            channel_name = channel_name.lower()
        return discord.utils.get(ctx.guild.channels, name=channel_name or HARD_READ_CHANNEL_NAME)

    async def get_read_count(self, ctx):
        try:
            msg_count = await self.bot.db.field("SELECT read_message_count FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            self.error.log_error(exc)
            return HARD_MESSAGE_COUNT
        return msg_count or HARD_MESSAGE_COUNT

    async def get_probot_member(self, ctx):
        try:
            bot_name = await self.bot.db.field("SELECT probot_name FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            self.error.log_error(exc)
            return HARD_PROBOT_NAME
        bot_name = bot_name or HARD_PROBOT_NAME
        for member in ctx.guild.members:
            if member.display_name == bot_name:
                return member
        return None

    async def read_embed_messages(self, ctx, count=None): 
        messages = []       
        read_channel = await self.get_read_channel(ctx)
        if read_channel is None:
            raise ConfigError("Could not get the ProBot read channel object")

        probot_member = await self.get_probot_member(ctx)
        if probot_member is None:
            raise ConfigError("Could not get the Probot user object")

        read_count = await self.get_read_count(ctx) if count is None else count            
        async for msg in read_channel.history(limit=int(read_count)):
            # Message responses to ProBot 'top' commands should exactly one embed
            if msg.author.id == probot_member.id and len(msg.embeds) == 1:
                messages.append(msg)

        return sorted(messages, key=lambda msg: msg.id)


