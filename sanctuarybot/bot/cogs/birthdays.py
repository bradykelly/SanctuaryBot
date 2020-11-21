from datetime import datetime
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog

BIRTHDAY_COMMANDS = ["set", "remove", "setuser"]

class Birthdays(BaseCog):
    """Commands to set up a birthday reminder/message"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)   

    @commands.group(
        name="birthday",
        aliases=["bday", "dob"],
        title="Commands to set up a birthday reminder/message", 
        help="Add, update or remove a user's birthday",
        brief="Birthday commands",
        usage="[set <YYYY-MM-DD>][remove][setuser <user-id> <YYYY-MM-DD>]"
    )
    async def birthday_command(self, ctx):
        if ctx.invoked_subcommand is None or (ctx.invoked_subcommand is not None 
            and ctx.invoked_subcommand.name not in BIRTHDAY_COMMANDS):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @birthday_command.error
    async def birthday_handler(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @birthday_command.command(
        name="set",
        aliases=["update"],
        help="Set your birthday",
        brief="Set your birthday",
        usage="<birthdate> (format `YYYY-MM-DD`)"    
    )
    async def set_command(self, ctx, birthdate):
        try:
            dob = datetime.strptime(birthdate, "%Y-%m-%d").date()
        except Exception as ex:
            await ctx.send(f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            try:
                await self.bot.db.execute("INSERT INTO member (member_id, date_of_birth) VALUES($1, $2) \
                    ON CONFLICT (member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth", 
                    ctx.message.author.id, dob)
            except Exception as ex:
                msg = ex.message
            else:
                await ctx.send(f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`")

    @set_command.error
    async def set_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument) and error.param.name == "birthday":
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")


def setup(bot):
    bot.add_cog(Birthdays(bot))    