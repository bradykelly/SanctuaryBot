from sanctuarybot import utils
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
        if ctx.invoked_subcommand is None or (ctx.invoked_subcommand is not None 
            and ctx.invoked_subcommand.name not in PROBOT_COMMANDS):
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
    async def read_command(self, ctx, count=None):
        pb_messages = await self._read_messages(ctx, count)
        await ctx.send(f"{len(pb_messages)} ProBot messages found")

    @read_command.error
    async def on_read_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")


    async def _read_messages(self, ctx, count=None): 
        messages = []       
        read_channel = await self.bot.probot.get_read_channel(ctx)
        if read_channel is not None:
            read_count = self.bot.probot.get_read_count(ctx) if count is None else count
            probot_member = await self.bot.probot.get_probot_member(ctx)
            if probot_member is not None:
                async for msg in read_channel.history(limit=int(read_count)):
                    if msg.author.id == probot_member.id:
                        messages.append(msg)
        return messages



def setup(bot):
    bot.add_cog(PbReader(bot))      