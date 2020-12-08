import asyncpg
import datetime
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog
from apscheduler.triggers.cron import CronTrigger
from sanctuarybot.utils.birthday_utils import BirthdayUtils

BIRTHDAY_COMMANDS = ["set", "clear", "public", "user", "show_messages"]

class Birthdays(BaseCog):
    """Commands to set up sending a birthday card on a user's birthday"""

    def __init__(self, bot):
        self.bot = bot
        self.utils = BirthdayUtils(self.bot)
        # TODO Uncomment when all this is working
        #self.bot.scheduler.add_job(self.utils.messages_job, CronTrigger(minute=0))

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)  

    # birthday command group
    @commands.group(
        name="birthday",
        aliases=["bday", "dob"],
        title="Commands to set up a birthday reminder/message", 
        help="Add, update or remove a user's birthday",
        brief="Birthday commands",
        usage="[set <YYYY-MM-DD>] [clear] [public [yes|no]] [user <user-id> <YYYY-MM-DD>]"
    )
    async def birthday_group(self, ctx):
        prefix = await self.bot.prefix(ctx.guild)
        if ctx.invoked_subcommand is None:
            dob = await self.bot.db.field("SELECT date_of_birth FROM member WHERE member_id = $1", ctx.author.id)            
            if dob is None:                
                await ctx.send(f"Your birthday is not set in our database. Use `{prefix}birthday set YYYY-MM-DD to set it.")
            else:
                await ctx.send(f"Your birthday is set to `{dob.strftime('%Y-%m-%d')}`. Use `{prefix}birthday clear` to clear the stored info.")
        elif ctx.invoked_subcommand.name not in BIRTHDAY_COMMANDS:
            await self.show_message_codeblock(ctx, self.format_usage(ctx, prefix), "Usage")

    @birthday_group.error
    async def birthday_handler(self, ctx, error):
        if isinstance(error, CommandNotFound):
            prefix = await self.bot.prefix(ctx.guild)
            await self.show_message_codeblock(ctx, self.format_usage(ctx, prefix), "Usage")


    # set command
    @birthday_group.command(
        name="set",
        aliases=["update"],
        help="Set your birthday in our database to get a birthday greeting on that date",
        brief="Set your birthday",
        usage="<YYYY-MM-DD>"    
    )
    async def set_command(self, ctx, birthdate):
        if not await self.check_over_18(ctx):
            return
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except Exception as ex:
            await ctx.send(f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            if await self._set_birthdate(ctx, ctx.author.id, dob):
                await ctx.send(f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`." +
                f"Although we store this data about you, you can clear it at any time with the `{self.bot.prefix}birthday clear` command.")
            else:
                await ctx.send(f"Could not set your birthday.")

    @set_command.error
    async def set_handler(self, ctx, error):
        await self.utils.handle_error(ctx, error, "birthdate", "An unhandled error occurred while trying to set your birthday")


    # user command
    #TODO Role/permissions check    
    @birthday_group.command(
        name="user",
        aliases=["setuser", "su"],
        help="Set a user's birthday in the database for that user to get a birthday greeting",
        brief="Set a user's birthday",
        usage="<user> <YYYY-MM-DD>"    
    )
    async def user_command(self, ctx, user: discord.User, birthdate):
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except Exception as ex:
            await ctx.send(f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            if await self._set_birthdate(ctx, user.id, dob):
                await ctx.send(f"The user's birthday has been set to `{dob.strftime('%Y-%m-%d')}`")
            else:
                await ctx.send(f"Could not set the user's birthday.")                

    @user_command.error
    async def user_handler(self, ctx, error):
        await self.utils.handle_error(ctx, error, "user", "An unhandled error occurred while trying to set the user's birthday") 
    

    # clear command
    @birthday_group.command(
        name="clear",
        aliases=["unset", "remove"],
        help="Clear your birthday from our database. You will no longer receive a birthday greeting",
        brief="Clear your birthday"    
    )
    async def clear_command(self, ctx):
        if not await self.check_over_18(ctx):
            return
        try:
            await self.bot.db.execute("UPDATE member SET date_of_birth = null WHERE member_id = $1", ctx.author.id)
        except asyncpg.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)
        else:
            await ctx.send(f"Your birthday has been cleared.")            

    @clear_command.error
    async def clear_handler(self, ctx, error):
        await self.utils.handle_error(ctx, error, None, "An unhandled error occuured while trying to clear your birthday")


    #public command
    @birthday_group.command(
        name="public", 
        help="Set whether you get a public or private birthday greeting",
        brief="Set public or private greeting",
        usage="[yes|no]"
    )
    async def public_command(self, ctx, yesNo):
        if not await self.check_over_18(ctx):
            return
        prefix = await self.bot.prefix(ctx.guild)
        if yesNo.lower() != "yes" and yesNo.lower() != "no":
            await self.show_message_codeblock(ctx, f"{prefix}birthday public [yes|no]", "Usage")
            return
        try:
            trueFalse = "TRUE" if yesNo.lower() == "yes" else "FALSE"             
            await self.bot.db.execute(f"UPDATE member SET birthday_greeting_public = {trueFalse} WHERE member_id = $1", ctx.author.id)
        except asyncpg.exceptions.PostgresError as ex:
            #TODO Do I need to call command_error or will it fire anyway
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)
        else:
            await ctx.send(f"Your birthday greeting has been set to {'public' if yesNo.lower() == 'yes' else 'private'}")        

    @public_command.error
    async def public_handler(self, ctx, error):
        await self.handle_error(ctx, error, "yesNo")


    # show_messages command
    #TODO Add a role/permissions check for this.
    @birthday_group.command(
        name="show_messages"  
    )
    async def show_messages_command(self, ctx):        
        if Birthdays.messages_busy:
            ctx.send("The Show Messages job is already busy running.")
            return
        try:
            await self.show_messages()
        except asyncpg.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)

    @show_messages_command.error
    async def show_messages_command_handler(self, ctx, error):
        await self.utils.handle_error(ctx, error)      


def setup(bot):
    bot.add_cog(Birthdays(bot))    