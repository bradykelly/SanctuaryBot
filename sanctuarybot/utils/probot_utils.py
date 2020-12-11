import discord
from sanctuarybot.exceptions import ConfigError
from sanctuarybot.models.probot_rank_item import ProbotLeaderItem

#TODO Document that admin should assign the nick 'Probot' to Probot to avoid uglies with special chars
HARD_PROBOT_NAME = 'ProBot ✨'
HARD_MESSAGE_COUNT = 50

class ProBotUtils():
    """Functions for reading and parsing messages from the ProBot bot"""

    def __init__(self, bot): 
        self.bot = bot

    async def get_read_channel(self, ctx): 
        """Gets the channel to read a message history from"""

        try:            
            channel_name = await self.bot.db.field("SELECT read_channel_name FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            error = self.bot.get_cog("Error")
            error.log_error(exc)
            return ctx.channel
        if channel_name is not None:
            channel_name = channel_name.lower()
        return discord.utils.get(ctx.guild.channels, name=channel_name or ctx.channel.name)

    async def get_read_count(self, ctx):
        """Gets the number of messages to read from the read channel"""

        try:
            msg_count = await self.bot.db.field("SELECT read_message_count FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            error = self.bot.get_cog("Error")
            error.log_error(exc)
            return HARD_MESSAGE_COUNT
        return msg_count or HARD_MESSAGE_COUNT

    async def get_probot_member(self, ctx):
        """Gets the ProBot member based from the database or the hard-coded member name"""

        try:
            bot_name = await self.bot.db.field("SELECT probot_name FROM probot_top WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            error = self.bot.get_cog("Error")
            error.log_error(exc)
            return HARD_PROBOT_NAME
        bot_name = bot_name or HARD_PROBOT_NAME
        for member in ctx.guild.members:
            if member.display_name == bot_name:
                return member
        return None

    async def read_message_history(self, ctx, count=None): 
        """Reads message history from the read channel"""

        read_channel = await self.get_read_channel(ctx)
        # If None is passed for count then get the db configured read_count
        read_count = await self.get_read_count(ctx) if count is None else int(count)
        # If 0 is passed as count then pass None to `history` to read all messages
        read_count = None if read_count == 0 else read_count
        messages = await read_channel.history(limit=read_count).flatten()

        return sorted(messages, key=lambda msg: msg.created_at)

    async def delete_messages(self, ctx, count):
        def is_not_pinned(m):
            return not m.pinned

        messages = await ctx.channel.purge(limit=count, check=is_not_pinned)
        return len(messages)        

    #trace
    async def parse_probot_messages(self, ctx, messages):
        """Parses ProBot leaderboard embeds in a list of messages"""

        count = 0
        probot_member = await self.get_probot_member(ctx)
        if probot_member is None:
            raise ConfigError("Could not get the Probot user object")

        for msg in messages:
            # Message responses to ProBot 'top' commands should have exactly one embed
            if msg.author.id != probot_member.id or len(msg.embeds) != 1:
                continue

            embed = msg.embeds[0]
            if not embed.author.name.endswith("Guild Score Leaderboards"):
                continue

            # Only the combined chat and voice embed has fields
            if len(embed.fields) > 0:
                continue

            ranks = self.parse_embed(embed)

            count += 1

        return count

    def parse_embed(self, embed):
        rank_items = []
        member_lines = embed.description.split("\n")            
        for line in member_lines:
            item = ProbotLeaderItem(embed.timestamp, embed.title, line)
            rank_items.append(item)

        return rank_items




