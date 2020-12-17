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
                await self.show_message_embed(ctx, await self.format_usage(ctx), "Usage")
                return
            if not await self._check_over_18(ctx):
                return
            prefix = await self.bot.prefix(ctx.guild)
            dob = await self.bot.db.field("SELECT date_of_birth FROM member WHERE guild_id = $1 AND member_id = $2", ctx.guild.id, ctx.author.id)            
            if dob is None:                
                await self.show_message_embed(ctx, f"Your birthday is not set in our database. Use `{prefix}birthday set YYYY-MM-DD` to set it.")
            else:
                await self.show_message_embed(ctx, f"Your birthday is set to `{dob.strftime('%Y-%m-%d')}`. Use `{prefix}birthday clear` to clear the stored info.")

    @birthday_group.error
    async def birthday_handler(self, ctx, error):
        if isinstance(error, CommandNotFound) or isinstance(error, MissingRequiredArgument):
            await self.show_message_embed(ctx, await self.format_usage(ctx), "Usage")


    # set command
    @birthday_group.command(
        name="set",
        aliases=["st", "update"],
        help="Set your birthday in our database to get a birthday greeting on that date",
        brief="Set your birthday greeting date",
        usage="<YYYY-MM-DD>"    
    )
    async def set_command(self, ctx, birthdate):
        if not await self._check_over_18(ctx):
            return
        prefix = await self.bot.prefix(ctx.guild)
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError as ex:
            await self.show_message_embed(ctx, f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            await self.utils.set_birthdate(ctx, ctx.author.id, dob)
            await self.show_message_embed(ctx, f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`. " +
                f"Although we store this data about you, you can clear it at any time with the `{prefix}birthday clear` command.")


    # setuser command 
    @birthday_group.command(
        name="setuser",
        aliases=["su", "user"],
        help="Set a user's birthday in the database for that user to get a birthday greeting on their birthday",
        brief="Set a user's birthday greeting date",
        usage="<user> <YYYY-MM-DD>"    
    )
    async def setuser_command(self, ctx, user: discord.User, birthdate):
        if not await self._check_botmaster(ctx):
            return
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError as ex:
            await self.show_message_embed(ctx, f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            await self.utils.set_birthdate(ctx, user.id, dob)
            await self.show_message_embed(ctx, f"The birthday for {user.mention} has been set to `{dob.strftime('%Y-%m-%d')}`")


    # clear command
    @birthday_group.command(
        name="clear",
        aliases=["unset", "remove"],
        help="Clear your birthday from our database. You will no longer receive a birthday greeting",
        brief="Clear your birthday"    
    )
    async def clear_command(self, ctx):
        await self.bot.db.execute("UPDATE member SET date_of_birth = NULL, \
            birthday_greeted_at = NULL, birthday_greeting_public = NULL WHERE guild_id = $1 AND member_id = $2", ctx.guild.id, ctx.author.id)
        await self.show_message_embed(ctx, f"Your birthday has been cleared.")            


    #public command
    @birthday_group.command(
        name="public",     
        help="Make your birthday greeting public",
        brief="Make your birthday greeting public"
    )
    async def public_command(self, ctx):
        if not await self._check_over_18(ctx):
            await self.show_message_embed(ctx, "You must be verified over 18 years to use this command.")
            return  
        await self.bot.db.execute(f"UPDATE member SET birthday_greeting_public = TRUE WHERE guild_id = $1 AND member_id = $2", ctx.guild.id, ctx.author.id)
        await self.show_message_embed(ctx, f"Your birthday greeting has been set to be public.")        


    # show_messages command
    @birthday_group.command(
        name="show_messages"  ,
        hidden=True
    )
    async def show_messages_command(self, ctx):     
        await self._check_botmaster(ctx)  
        if BirthdayUtils.messages_job_running:
            await self.show_message_embed(ctx, "The show_messages job is busy running", "show_messages")
            return 
        await self.utils.show_messages()


    async def _check_over_18(self, ctx):
        if self.over18Roles is None:
            self.over18Roles = await self.bot.roles.get_over_18_roles()
        guildRoles = self.over18Roles[ctx.guild.name]
        hasRole = False
        for role in guildRoles:
            if role in ctx.author.roles:
                hasRole = True
                break
        if not hasRole:
            await self.show_message_embed(ctx, "You must be verified over 18 years old to use this command.")
            return False
        else:
            return True

    async def _check_botmaster(self, ctx):
        if self.botMasterRoles is None:
            self.botMasterRoles = await self.bot.roles.get_botmaster_roles()
        guildRoles = self.botMasterRoles[ctx.guild.name]
        hasRole = False
        for role in guildRoles:
            if role in ctx.author.roles:
                hasRole = True
                break
        if not hasRole:
            await self.show_message_embed(ctx, "You must have one of the BotMaster roles to use this command.")
            return False
        else:
            return True




def setup(bot):
    bot.add_cog(Birthdays(bot))    