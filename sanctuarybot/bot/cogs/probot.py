import asyncpg
import datetime
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog


PROBOT_COMMANDS = ["read", "clear"]

class PbReader(BaseCog):
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
        usage="[read [read_count]] | [clear[clear_count]]")
    async def probot_group(self, ctx):
        if ctx.invoked_subcommand.name not in PROBOT_COMMANDS:
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @probot_group.error
    async def on_probot_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument) or isinstance(error, CommandNotFound):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @probot_group.command(
        name="read",
        aliases=["rd"],
        usage="[count]"
    )
    async def read_command(self, ctx, count):
        pb_messages = []
        #TODO #5 Get total message count if 'count' == zero
        #TODO #6 Get default message count if 'count' not provided
        #TODO #7 Get configured channel id for probot commands
        async for msg in ctx.channel.history(limit=count):
            #TODO #8 Look up ProBot (or configured bot name) user id in guild users
            if msg.author.id == 282859044593598464:
                pb_messages.append(msg)
        await ctx.send(f"{len(pb_messages)} ProBot messages found")

    @read_command.error
    async def on_read_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")


def setup(bot):
    bot.add_cog(PbReader(bot))      