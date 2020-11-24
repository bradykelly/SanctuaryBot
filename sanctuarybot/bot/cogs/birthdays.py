import asyncpg
import datetime
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog
from apscheduler.triggers.cron import CronTrigger


BIRTHDAY_COMMANDS = ["set", "clear", "public", "user", "show_messages"]

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
        usage="[set <YYYY-MM-DD>] [clear] [public [yes|no]] [user <user-id> <YYYY-MM-DD>]"
    )
    async def birthday_command(self, ctx):
        prefix = await self.bot.prefix(ctx.guild)
        if ctx.invoked_subcommand is None:
            dob = await self.bot.db.field("SELECT date_of_birth FROM member WHERE member_id = $1", ctx.author.id)            
            if dob is None:                
                await ctx.send(f"Your birthday is not set in our database. Use `{prefix}birthday set YYYY-MM-DD to set it.")
            else:
                await ctx.send(f"Your birthday is set to `{dob.strftime('%Y-%m-%d')}`. Use `{prefix}birthday clear` to clear it.")
        elif ctx.invoked_subcommand.name not in BIRTHDAY_COMMANDS:
            await self.show_message_codeblock(ctx, self.format_usage(ctx, prefix), "Usage")

    @birthday_command.error
    async def birthday_handler(self, ctx, error):
        if isinstance(error, CommandNotFound):
            prefix = await self.bot.prefix(ctx.guild)
            await self.show_message_codeblock(ctx, self.format_usage(ctx, prefix), "Usage")


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
            if await self.set_birthdate(ctx.author.id, dob):
                await ctx.send(f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`")

    @set_command.error
    async def set_handler(self, ctx, error):
        prefix = await self.bot.prefix(ctx.guild)
        if isinstance(error, MissingRequiredArgument) and error.param.name == "birthdate":
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")
        else:
            msg = error.message if isinstance(error, Exception) else f"Type of error:{str(error)}"                
            await ctx.send(f"An unhandled error occurred while trying to set your birthday: {msg}")

    @birthday_command.command(
        name="user",
        aliases=["setuser"],
        help="Set a user's birthday",
        brief="Set a user's birthday",
        usage="<user> <birthdate> (format `YYYY-MM-DD`)"    
    )
    async def user_command(self, ctx, user: discord.User, birthdate):
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except Exception as ex:
            await ctx.send(f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            if await self.set_birthdate(user.id, dob):
                await ctx.send(f"The user's birthday has been set to `{dob.strftime('%Y-%m-%d')}`")

    @user_command.error
    async def user_handler(self, ctx, error):
        prefix = await self.bot.prefix(ctx.guild)
        if isinstance(error, MissingRequiredArgument) and error.param.name == "birthdate":
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")
        else:
            msg = error.message if isinstance(error, Exception) else f"Type of error:{str(error)}"                
            await ctx.send(f"An unhandled error occurred while trying to set the user's birthday: {msg}")
    

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


    @birthday_command.command(
        name="public", 
        help="Set whether you get a public or private birthday greeting",
        brief="Set public or private birthday greeting"   ,
        usage="[yes|no]"
    )
    async def public_command(self, ctx, yesNo):
        prefix = await self.bot.prefix(ctx.guild)
        if yesNo.lower() != "yes" and yesNo.lower() != "no":
            await self.show_message_codeblock(ctx, f"{prefix}birthday public [yes|no]", "Usage")
            return
        try:
            trueFalse = "TRUE" if yesNo.lower() == "yes" else "FALSE"             
            await self.bot.db.execute(f"UPDATE member SET birthday_greeting_public = {trueFalse} WHERE member_id = $1", ctx.author.id)
        except asyncpg.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)
        else:
            await ctx.send(f"Your birthday greeting has been set to {'public' if yesNo.lower() == 'yes' else 'private'}")        

    @public_command.error
    async def public_handler(self, ctx, error):
        prefix = await self.bot.prefix(ctx.guild)
        if isinstance(error, MissingRequiredArgument) and error.param.name == "yesNo":
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")
        else:
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

    @show_messages_command.error
    async def show_messages_command_handler(self, ctx, error):
        msg = error.message if isinstance(error, Exception) else f"Type of error: {str(error)}"                
        await ctx.send(f"An unhandled error occuured while trying to show birthday messages: `{msg}`")        

    async def _show_messages(self):
        bdayRecs = await self.bot.db.records("SELECT member_id, date_of_birth FROM member \
            WHERE birthday_greeting_time IS NULL AND date_of_birth = $1", datetime.date.today())
        for rec in bdayRecs:
            member = self.bot.get_user(rec["member_id"])
            await member.send(embed=self.build_birthday_message())
            await self.bot.db.execute("UPDATE member SET birthday_greeting_time = $1 WHERE member_id = $2", datetime.datetime.now(), rec["member_id"])
        await self.bot.db.execute("UPDATE member SET birthday_greeting_time = null WHERE date(birthday_greeting_time) < $1", datetime.date.today())         

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

    async def set_birthdate(self, user_id, dob):    
        try:
            await self.bot.db.execute("INSERT INTO member (member_id, date_of_birth) VALUES($1, $2) \
                ON CONFLICT (member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth, birthday_greeting_time = NULL", 
                user_id, dob)
            return True
        except asyncpg.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)
            return False    

    def build_birthday_message(self):
        self.bot.embed.build(
            title="Happy Birthday!", 
            description="The Sanctuary community wishes you a very happy birthday",
            url="http://sancturaybot.co.za/help?command=birthday",
            author_url="http://sancturaybot.co.za",
            image="file://D:/Personal/Python+Projects/SanctuaryBot/images/bday1.jpg"
        )            


def setup(bot):
    bot.add_cog(Birthdays(bot))    