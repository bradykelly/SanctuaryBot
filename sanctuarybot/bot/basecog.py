from discord.ext import commands


class BaseCog(commands.Cog):
    """Base class for application cogs in this bot"""

    def __init__(self, bot):
        self.bot = bot

    def format_usage(self, ctx, prefix=None):
        '''
        Contructs a formatted usage string for a command.
        '''
        usg = f"{prefix if prefix is not None else ''}{ctx.command.name} {ctx.command.usage}"
        return usg

    async def show_message_codeblock(self, ctx, message, title=None):
        '''
        Shows the user a message in the format of a code block
        '''
        msg = "```\n"
        if title is not None:
            msg += title + "\n\n"
        msg += message
        msg += "\n```"
        await ctx.send(msg)    
