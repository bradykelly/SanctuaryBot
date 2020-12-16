from asyncpg.exceptions._base import PostgresError
from discord import guild
from sanctuarybot.config import Config
from sanctuarybot.utils.roles import Roles
import datetime
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from sanctuarybot.bot.basecog import BaseCog
from apscheduler.triggers.cron import CronTrigger
from sanctuarybot.utils.birthday_utils import BirthdayUtils

BIRTHDAY_COMMANDS = ["set", "clear", "public", "user", "show_messages"]

class Birthdays(BaseCog):
    """Commands to set up sending a birthday card message on a user's birthday"""

    def __init__(self, bot):
        self.bot = bot
        self.utils = BirthdayUtils(self.bot)
        self.over18Roles = None
        self.botMasterRoles = None
        # TODO Uncomment job sched when all this is working
        #self.bot.scheduler.add_job(self.utils.messages_job, CronTrigger(minute=0))

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)  

    # birthday command group
    @commands.group(
        name="birthday",
        aliases=["bd", "bday", "dob"],
        title="Commands to set up a greeting for your birthday", 
        help="Add, update or remove your birthday",
        brief="Birthday greeting commands",
        usage="set <YYYY-MM-DD> | clear | public <yes|no>"
    )
    async def birthday_group(self, ctx):            
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed is not None and not ctx.subcommand_passed in BIRTHDAY_COMMANDS:
                await self.show_message_codeblock(ctx, await self.format_usage(ctx), "Usage")
                return
            await self._check_over_18(ctx)
            prefix = await self.bot.prefix(ctx.guild)
            dob = await self.bot.db.field("SELECT date_of_birth FROM member WHERE member_id = $1", ctx.author.id)            
            if dob is None:                
                await self.show_message_codeblock(ctx, f"Your birthday is not set in our database. Use `{prefix}birthday set YYYY-MM-DD` to set it.")
            else:
                await self.show_message_codeblock(ctx, f"Your birthday is set to `{dob.strftime('%Y-%m-%d')}`. Use `{prefix}birthday clear` to clear the stored info.")

    @birthday_group.error
    async def birthday_handler(self, ctx, error):
        if isinstance(error, CommandNotFound) or isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, await self.format_usage(ctx), "Usage")


    # set command
    @birthday_group.command(
        name="set",
        aliases=["st", "update"],
        help="Set your birthday in our database to get a birthday greeting on that date",
        brief="Set your birthday greeting date",
        usage="<YYYY-MM-DD>"    
    )
    async def set_command(self, ctx, birthdate):
        self._check_over_18(ctx)
        prefix = await self.bot.prefix(ctx.guild)
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError as ex:
            await self.show_message_codeblock(ctx, f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            await self.utils.set_birthdate(ctx, ctx.author.id, dob)
            await self.show_message_codeblock(ctx, f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`. Use `{prefix}help {ctx.command}` for more information. " +
                f"Although we store this data about you, you can clear it at any time with the `{prefix}birthday clear` command.")

    @set_command.error
    async def set_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, await self.format_usage(ctx), "Usage")


    # setuser command 
    @birthday_group.command(
        name="setuser",
        aliases=["su", "user"],
        help="Set a user's birthday in the database for that user to get a birthday greeting on that date",
        brief="Set a user's birthday greeting date",
        usage="<user> <YYYY-MM-DD>"    
    )
    #TODO Check if coersion to User works
    async def setuser_command(self, ctx, user: discord.User, birthdate):
        self._check_over_18(ctx)
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError as ex:
            await ctx.send(f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            await self.utils.set_birthdate(ctx, user.id, dob)
            await self.show_message_codeblock(ctx, f"The user's birthday has been set to `{dob.strftime('%Y-%m-%d')}`")

    @setuser_command.error
    async def user_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, await self.format_usage(ctx), "Usage")


    # clear command
    @birthday_group.command(
        name="clear",
        aliases=["unset", "remove"],
        help="Clear your birthday from our database. You will no longer receive a birthday greeting",
        brief="Clear your birthday"    
    )
    async def clear_command(self, ctx):
        await self.bot.db.execute("UPDATE member SET date_of_birth = NULL, \
            birthday_greeting_time = NULL WHERE member_id = $1", ctx.author.id)
        await self.show_message_codeblock(ctx, f"Your birthday has been cleared.")            


    #public command
    @birthday_group.command(
        name="public", 
        help="Set whether you get a public or private birthday greeting",
        brief="Set public or private greeting",
        usage="[yes|no]"
    )
    async def public_command(self, ctx, yesNo):
        if not await self.check_over_18(ctx):
            await ctx.send("You must be verified over 18 years to use this command.")
            return
        prefix = await self.bot.prefix(ctx.guild)
        if yesNo.lower() != "yes" and yesNo.lower() != "no":
            await self.show_message_codeblock(ctx, f"{prefix}birthday public [yes|no]", "Usage")
            return
        trueFalse = "TRUE" if yesNo.lower() == "yes" else "FALSE"             
        await self.bot.db.execute(f"UPDATE member SET birthday_greeting_public = {trueFalse} WHERE member_id = $1", ctx.author.id)
        await ctx.send(f"Your birthday greeting has been set to {'public' if yesNo.lower() == 'yes' else 'private'}")        

    @public_command.error
    async def public_handler(self, ctx, error):
        await self.handle_error(ctx, error, "yesNo")


    # show_messages command
    @birthday_group.command(
        name="show_messages"  ,
        hidden=True
    )
    async def show_messages_command(self, ctx):     
        await self._check_botmaster(ctx)   
        await self.utils.show_messages()


    async def _check_over_18(self, ctx):
        if self.over18Roles is None:
            self.over18Roles = await self.bot.roles.get_over_18_roles()
        guildRoles = self.over18Roles[ctx.guild.id]
        hasRole = False
        for role in guildRoles:
            if role in ctx.author.roles:
                hasRole = True
                break
        if not hasRole:
            self.show_message_codeblock(ctx, "You must be verified over 18 years old to use this command.")

    async def _check_botmaster(self, ctx):
        if self.botMasterRoles is None:
            self.botMasterRoles = await self.bot.roles.get_botmaster_roles()
        guildRoles = self.botMasterRoles[ctx.guild.id]
        hasRole = False
        for role in guildRoles:
            if role in ctx.author.roles:
                hasRole = True
                break
        if not hasRole:
            self.show_message_codeblock(ctx, "You must have one of the BotMaster roles to use this command.")




def setup(bot):
    bot.add_cog(Birthdays(bot))    