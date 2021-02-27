import discord
from sanctuarybot.exceptions import ConfigError
from sanctuarybot.models.probot_rank_item import ProbotRankItem
from sanctuarybot.utils.baseutil import BaseUtil

#TODO Document that admin should assign the nick 'Probot' to Probot to avoid uglies with special chars
HARD_PROBOT_NAME = 'ProBot ✨'
HARD_MESSAGE_COUNT = 20

class ProBotUtils(BaseUtil):
    """Functions for reading and parsing messages from the ProBot bot"""

    def __init__(self, bot): 
        self.bot = bot

    async def get_read_count(self, ctx):
        """Gets the number of messages to read/clear from the channel"""

        try:
            msg_count = await self.bot.db.field("SELECT read_message_count FROM probot WHERE guild_id = $1", ctx.guild.id)
        except Exception as exc:
            return HARD_MESSAGE_COUNT
        return msg_count or HARD_MESSAGE_COUNT

    async def get_probot_member(self, ctx):
        """Gets the ProBot member based on the database or the hard-coded member name"""

        bot_name = None
        try:
            bot_name = await self.bot.db.field("SELECT probot_name FROM probot WHERE guild_id = $1", ctx.guild.id)
        except Exception:
            pass
        bot_name = bot_name or HARD_PROBOT_NAME
        for member in ctx.guild.members:
            if member.display_name == bot_name:
                return member
        return None

    async def read_message_history(self, ctx, count=None): 
        """Reads message history from the current channel"""

        # If None is passed for count then get the db configured read_count
        read_count = await self.get_read_count(ctx) if count is None else int(count)
        # If 0 is passed as count then pass None to `history` to read all messages
        read_count = None if read_count == 0 else read_count
        messages = await ctx.channel.history(limit=read_count).flatten()

        return sorted(messages, key=lambda msg: msg.created_at)

    async def delete_messages(self, ctx, count):
        def is_not_pinned(m):
            return not m.pinned

        # If None is passed for count then get the db configured read_count
        clear_count = await self.get_read_count(ctx) if count is None else int(count)
        # If 0 is passed as count then pass None to `history` to read all messages
        clear_count = None if clear_count == 0 else clear_count

        messages = await ctx.channel.purge(limit=clear_count, check=is_not_pinned)
        return len(messages)        

    async def import_probot_messages(self, ctx, messages):
        """Parses and imports ProBot leaderboard embeds from a list of messages"""

        count = 0
        probot_member = await self.get_probot_member(ctx)
        if probot_member is None:
            raise ConfigError("Could not get the Probot user object")

        for msg in messages:
            # leaderboard messages should have exactly one embed
            if msg.author.id != probot_member.id or len(msg.embeds) != 1:
                continue

            embed = msg.embeds[0]
            if not embed.author.name.endswith("Guild Score Leaderboards"):
                continue

            # Only the combined chat and voice embed has fields. We want chat or voice separately.
            if len(embed.fields) > 0:
                continue

            rank_items = self.parse_embed(embed)

            count += 1

        return count

    def parse_embed(self, embed):
        rank_items = []
        member_lines = embed.description.split("\n")            
        for line in member_lines:
            item = ProbotRankItem(embed.timestamp, embed.title, line)
            rank_items.append(item)

        return rank_items

    def write_rank_items(self, guildId, new_rank_items):
        for new_item in  new_rank_items:
            self.bot.db.execute("INSERT probot_import (guild_id, time, type, part, member_id, rank, points) VALUES ($1, $2, $3, $4, $5, $6, $7", 
                guildId, new_item.timestamp, new_item.type, new_item.part, new_item.member_id, new_item.rank, new_item.points)
            

        




