import asyncpg
import datetime
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog
from apscheduler.triggers.cron import CronTrigger


BIRTHDAY_COMMANDS = ["set", "clear", "user", "show_messages"]

class Birthdays(BaseCog):
    """Commands to set up a birthday reminder/message"""

    messages_busy = False

    def __init__(self, bot):
        self.bot = bot
        self.bot.scheduler.add_job(self.messages_job, CronTrigger(minute=0))

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
        usage="[set <YYYY-MM-DD>][clear][user <user-id> <YYYY-MM-DD>]"
    )
    async def birthday_command(self, ctx):
        if ctx.invoked_subcommand is None:
            dob = await self.bot.db.field("SELECT date_of_birth FROM member WHERE member_id = $1", ctx.author.id)
            prefix = await self.bot.prefix(ctx.guild)
            if dob is None:                
                await ctx.send(f"Your birthday is not set in our database. Use `{prefix}birthday set YYYY-MM-DD to set it.")
            else:
                await ctx.send(f"Your birthday is set to `{dob.strftime('%Y-%m-%d')}`. Use `{prefix}birthday clear` to clear it.")
        elif ctx.invoked_subcommand.name not in BIRTHDAY_COMMANDS:
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
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except Exception as ex:
            await ctx.send(f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            try:
                await self.bot.db.execute("INSERT INTO member (member_id, date_of_birth) VALUES($1, $2) \
                    ON CONFLICT (member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth, birthday_greeting_time = NULL", 
                    ctx.message.author.id, dob)
            except asyncpg.exceptions.PostgresError as ex:
                error_cog = self.bot.get_cog("Error")
                await error_cog.command_error(ctx, ex)
            else:
                await ctx.send(f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`")

    @set_command.error
    async def set_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument) and error.param.name == "birthday":
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")
        else:
            msg = error.message if isinstance(error, Exception) else f"Type of error:{str(error)}"                
            await ctx.send(f"An unhandled error occuured while trying to clear your birthday: {msg}")
    

    @birthday_command.command(
        name="clear",
        aliases=["unset", "remove"],
        help="Clear your birthday from our database",
        brief="Clear stored birthday"    
    )
    async def clear_command(self, ctx):
        try:
            await self.bot.db.execute("UPDATE member SET date_of_birth = null WHERE member_id = $1", ctx.author.id)
        except asyncpg.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)
        else:
            await ctx.send(f"Your birthday has been cleared.")            

    @clear_command.error
    async def clear_handler(self, ctx, error):
        msg = error.message if isinstance(error, Exception) else f"Type of error: {str(error)}"                
        await ctx.send(f"An unhandled error occuured while trying to clear your birthday: `{msg}`")

    #TODO Add a role check for this.
    @birthday_command.command(
        name="show_messages"  
    )
    async def show_messages_command(self, ctx):
        if Birthdays.messages_busy:
            ctx.send("The Show Messages job is already busy running.")
            return
        try:
            await self._show_messages()
        except asyncpg.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)

    async def messages_job(self):
        Birthdays.messages_busy = True
        try:
            await self._show_messages()
        except Exception as ex:
            print(f"Exception running messages job: {ex.message}")
            error_cog = self.bot.get_cog("Error")
            await error_cog.log_error(ex)
        finally:
            Birthdays.messages_busy = False

    async def _show_messages(self):
        bdayRecs = await self.bot.db.records("SELECT member_id, date_of_birth FROM member \
            WHERE birthday_greeting_time IS NULL AND date_of_birth = $1", datetime.date.today())
        for rec in bdayRecs:
            member = self.bot.get_user(rec["member_id"])
            await member.send(f"Happy birthday, {member.name}!")
            await self.bot.db.execute("UPDATE member SET birthday_greeting_time = $1 WHERE member_id = $2", datetime.datetime.now(), rec["member_id"])
        await self.bot.db.execute("UPDATE member SET birthday_greeting_time = null WHERE date(birthday_greeting_time) < $1", datetime.date.today())         



def setup(bot):
    bot.add_cog(Birthdays(bot))    