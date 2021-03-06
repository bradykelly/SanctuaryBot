import discord


class OutputUtils():
    def __init__(self, bot):
        self.bot = bot

    async def format_usage(self, ctx):
        prefix = await self.bot.prefix(ctx.guild)
        usg = f"{ctx.command.name} {ctx.command.usage}"
        return usg

    async def show_message_embed(self, ctx, message, title=None): 
        embed  = discord.Embed(title=title, description=message)
        await ctx.send(embed=embed)    