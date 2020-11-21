from discord.ext import commands
from sanctuarybot import config
from sanctuarybot.bot.basecog import BaseCog


class Config(BaseCog):
    """Bot config commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self) 

    @commands.command(
        name="prefix",
        help=f"Gets or sets the command prefix for this server."
    )     
    async def prefix_command(self, ctx, newPrefix=None):
        curPrefix = await self.bot.prefix(ctx.guild)
        if newPrefix is None:
            await ctx.send(f"The {config.Config.BOT_NAME} command prefix in this server is `{curPrefix}`. To change it, use `{curPrefix}prefix <new prefix>`.")
        else:
            if len(newPrefix) == 0 or len(newPrefix) > config.MAX_PREFIX_LEN:
                await ctx.send(f"The command prefix must be \between 1 and {config.MAX_PREFIX_LEN} characters long")
                return   
            await self.bot.db.execute("UPDATE guild_config \
                SET command_prefix = $2 WHERE guild_id = $1", ctx.guild.id, newPrefix) 
            await ctx.send(f"The {config.Config.BOT_NAME} prefix in this server is now `{newPrefix}`.")
         

def setup(bot):
    bot.add_cog(Config(bot))                          