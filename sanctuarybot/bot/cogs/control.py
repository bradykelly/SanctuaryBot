from discord.ext import commands
from sanctuarybot.config import Config
from sanctuarybot.bot.basecog import BaseCog


class Control(BaseCog):
    """Bot control commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)              

    @commands.command(
        name="leave_server",
        aliases=["exit_server"],
        help=f"Leaves this server permanently. {Config.BOT_NAME} will need to be invited in order to join this server again."
    )
    async def leave_command(self, ctx):
        guild = ctx.guild
        guild.leave()            

    @commands.command(
        name="shutdown",
        help = f"Shuts {Config.BOT_NAME} down. The bot will have to be manually restarted via its web interface."
    )
    async def shutdown_command(self, ctx):
        await self.bot.shutdown()        

def setup(bot):
    bot.add_cog(Control(bot))              