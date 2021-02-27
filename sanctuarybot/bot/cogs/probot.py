import asyncpg
import datetime
import discord
from discord.errors import Forbidden, HTTPException, NotFound
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog
from sanctuarybot.utils.probot import ProBotUtils


PROBOT_COMMANDS = ["import", "clear"]

class Probot(BaseCog):
    """Commands to parse output from the ProBot leaderboards"""

    def __init__(self, bot):
        self.bot = bot
        self.probot = ProBotUtils(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)

    @commands.group(
        name="probot",
        aliases=["pb", "pbot"],
        brief="Commands to work with Probot",
        usage="import [read_count] | clear [clear_count]")
    async def probot_group(self, ctx):
        
        # This condition doesn't automatically raise CommandNotFound, thus doesn't trigger @probot_group.error
        if ctx.subcommand_passed is not None and not ctx.subcommand_passed in PROBOT_COMMANDS:
            raise CommandNotFound

    @probot_group.error
    async def on_probot_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await self.output.show_message_embed(ctx, await self.output.format_usage(ctx), "Usage")

    @probot_group.command(
        name="import",
        aliases=["imp", "ip"],
        usage="[read_count]"
    )
    async def import_command(self, ctx, count: int=None):
        channel_messages = await self.probot.read_message_history(ctx, count)
        embed_count = await self.probot.import_probot_leaderboards(ctx, channel_messages)
        await self.output.show_message_embed(ctx, f"{embed_count} ProBot leaderboard messages imported", "import")

    @import_command.error
    async def on_clear_error(self, ctx, error):
        await self.output.show_message_embed(ctx, 
            f"Command failed: {error.message if hasattr(error, 'message') else str(error)}", "clear")


    @probot_group.command(
        name="clear",
        aliases=["delete", "del", "cl"],
        usage="[count]"
    )
    async def clear_command(self, ctx, count=None):        
        messages = await self.probot.read_message_history(ctx, count)
        await ctx.send(f"Clearing {len(messages)} messages...")
        count = await self.probot.delete_messages(ctx, count)
        await self.output.show_message_embed(ctx, f"{count} Messages cleared", "clear")

    @clear_command.error
    async def on_clear_error(self, ctx, error):
        if isinstance(error, Forbidden) or isinstance(error, NotFound) or isinstance(error, HTTPException):
            await self.output.show_message_embed(ctx, 
                f"Command failed: {error.message if hasattr(error, 'message') else str(error)}", "clear")


def setup(bot):
    bot.add_cog(Probot(bot))      