from sanctuarybot.models.probot_leaderboard import ProbotLeaderboard
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

    async def import_probot_leaderboards(self, ctx, messages):

        leaderboards = []
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

            # The combined chat and voice embed has fields. 
            # We want chat or voice separately, these have no fields.
            if len(embed.fields) > 0:
                continue

            leaderboards.append(ProbotLeaderboard(embed))

        await self.write_leaderboards(leaderboards)
        return len(leaderboards)

    async def write_leaderboards(self, guildId, leaderboards):
        for board in leaderboards:
            for item in board.items:
                member_row = await self.bot.db.record("SELECT chat_points, voice_points FROM probot_points WHERE guild_id = $1 \
                    AND member_id = $2", board.guild_id, item.member_id)
                if member_row is None:
                    await self.bot.db.execute("INSERT INTO probot_points (guild_id, member_id, chat_points, voice_points) VALUES( \
                        $1, $2, $3, $4)", board.guild_id, item.member_id, item.chat_points, item.voice_points)
                else:
                    if board.type.lower() == "chat" and item.chat_points > member_row["chat_points"]:
                        await self.bot.db.execute("UPDATE probot_points SET chat_points = $1 \
                            WHERE guild_id = $2 and member_id = $3", item.chat_points, board.guild_id, item.member_id)
                    elif board.type.lower() == "voice" and item.voice_points > member_row["voice_points"]:
                        await self.bot.db.execute("UPDATE probot_points SET voice_points = $1 \
                            WHERE guild_id = $2 and member_id = $3", item.voice_points, board.guild_id, item.member_id)
            

        





