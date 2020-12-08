import asyncpg
import datetime
import discord
from discord.errors import Forbidden, HTTPException, NotFound
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog


PROBOT_COMMANDS = ["read", "clear"]

class ProbotReader(BaseCog):
    """Commands to parse xp output from the ProBot `top` commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)

    @commands.group(
        name="probot",
        aliases=["pb", "pbot"],
        brief="Commands to work with Probot",
        usage="[read [read_count]] | [clear[clear_count]]")
    async def probot_group(self, ctx):
        if ctx.invoked_subcommand is None or (ctx.invoked_subcommand is not None 
            and ctx.invoked_subcommand.name not in PROBOT_COMMANDS):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @probot_group.error
    async def on_probot_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @probot_group.command(
        name="read",
        aliases=["rd"],
        usage="[count]"
    )
    async def read_command(self, ctx, count: int=None):
        channel_messages = await self.bot.probot.read_message_history(ctx, count)
        count = await self.bot.probot.parse_probot_messages(ctx, channel_messages)
        await self.show_message_codeblock(ctx, f"{count} ProBot embed messages parsed", "read")

    @probot_group.command(
        name="clear",
        aliases=["delete", "del", "cl"],
        usage="[count]"
    )
    async def clear_command(self, ctx, count: int=None):
        messages = await self.bot.probot.read_message_history(ctx, count)
        await ctx.send(f"Clearing {len(messages)} messages...")
        count = await self.bot.probot.delete_messages(ctx, count)
        await self.show_message_codeblock(ctx, f"{count} Messages cleared", "clear")

    @clear_command.error
    async def on_clear_error(self, ctx, error):
        if isinstance(error, Forbidden) or isinstance(error, NotFound) or isinstance(error, HTTPException):
            await self.show_message_codeblock(ctx, 
                f"Command failed: {error.message if hasattr(error, 'message') else str(error)}", "clear")


def setup(bot):
    bot.add_cog(ProbotReader(bot))      