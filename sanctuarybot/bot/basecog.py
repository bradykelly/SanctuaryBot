from discord.ext import commands


class BaseCog(commands.Cog):
    """Base class for application cogs in this bot"""

    def __init__(self, bot):
        self.bot = bot

    async def format_usage(self, ctx):
        prefix = await self.bot.prefix(ctx.guild)
        usg = f"{ctx.command.name} {ctx.command.usage}"
        return usg

    async def show_message_codeblock(self, ctx, message, title=None):
        msg = "```\n"
        if title is not None:
            msg += title + "\n\n"
        msg += message
        msg += "\n```"
        await ctx.send(msg)    
