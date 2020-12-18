import datetime
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
from apscheduler.triggers.cron import CronTrigger
from sanctuarybot.bot.basecog import BaseCog
from sanctuarybot.utils.birthday import BirthdayUtils

BIRTHDAY_COMMANDS = ["set", "clear", "public", "private", "setuser", "send_messages"]

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
        usage="set <YYYY-MM-DD> | clear | public | private"
    )
    async def birthday_group(self, ctx):            
        # Only execute if the sub-command is blank, i.e. a birthday query
        if ctx.invoked_subcommand is None:

            # Somehow this condition doesn't raise CommandNotFound.
            if ctx.subcommand_passed is not None and not ctx.subcommand_passed in BIRTHDAY_COMMANDS:
                await self.bot.output.show_message_embed(ctx, await self.bot.output.format_usage(ctx), "Usage")
                return

            if not await self.bot.roles.check_over_18(ctx):
                return

            prefix = await self.bot.prefix(ctx.guild)
            dob = await self.utils.get_birthdate(ctx)
            if dob is None:                
                await self.bot.output.show_message_embed(ctx, f"Your birthday is not set in our database. "
                    + f"Use `{prefix}birthday set YYYY-MM-DD` to set it.", "Birthday")
            else:
                await self.bot.output.show_message_embed(ctx, f"Your birthday is set to `{dob.strftime('%Y-%m-%d')}`. "
                    + f"Use `{prefix}birthday set YYYY-MM-DD` to change it or use `{prefix}birthday clear` to clear the stored info.", "Birthday")

    @birthday_group.error
    async def birthday_handler(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await self.bot.output.show_message_embed(ctx, await self.bot.output.format_usage(ctx), "Usage")


    # set command
    @birthday_group.command(
        name="set",
        aliases=["st", "update"],
        help="Set your birthday in our database to get a birthday greeting on that date",
        brief="Set your birthday greeting date",
        usage="<YYYY-MM-DD>"    
    )
    async def set_command(self, ctx, birthdate):
        if not await self.bot.roles.check_over_18(ctx):
            return
        
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError as ex:
            await self.bot.output.show_message_embed(ctx, f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.", "Usage")
        else:            
            await self.utils.set_birthdate(ctx, ctx.author.id, dob)
            prefix = await self.bot.prefix(ctx.guild)
            await self.bot.output.show_message_embed(ctx, f"Your birthday has been set to `{dob.strftime('%Y-%m-%d')}`. " +
                f"Although we store this data about you, you can clear it at any time with the `{prefix}birthday clear` command.", "Set")


    # setuser command 
    @birthday_group.command(
        name="setuser",
        aliases=["su", "user"],
        help="Set a user's birthday in the database for that user to get a birthday greeting on their birthday",
        brief="Set a user's birthday greeting date",
        usage="<user> <YYYY-MM-DD>"    
    )
    async def setuser_command(self, ctx, user: discord.User, birthdate):
        if not await self.bot.roles.check_botmaster(ctx):
            return
        try:
            dob = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError as ex:
            await self.bot.output.show_message_embed(ctx, f"Birthday value `{birthdate}` is not in a valid format. Please use format `YYYY-MM-DD`.")
        else:
            await self.utils.set_birthdate(ctx, user.id, dob)
            await self.bot.output.show_message_embed(ctx, f"The birthday for {user.mention} has been set to `{dob.strftime('%Y-%m-%d')}`")


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
        await self.bot.output.show_message_embed(ctx, f"Your birthday has been cleared.", "Clear")            


    #public command
    @birthday_group.command(
        name="public",     
        help="Make your birthday greeting public",
        brief="Make your birthday greeting public"
    )
    async def public_command(self, ctx):
        if not await self.bot.roles.check_over_18(ctx):
            await self.bot.output.show_message_embed(ctx, "You must be verified over 18 years to use this command.", "Public")
            return  
        await self.bot.db.execute(f"UPDATE member SET birthday_greeting_public = TRUE WHERE guild_id = $1 AND member_id = $2", ctx.guild.id, ctx.author.id)
        await self.bot.output.show_message_embed(ctx, f"Your birthday greeting has been set to be public.", "Public")        


    #private command
    @birthday_group.command(
        name="private",     
        help="Make your birthday greeting private",
        brief="Make your birthday greeting private"
    )
    async def private_command(self, ctx):
        if not await self.bot.roles.check_over_18(ctx):
            await self.bot.output.show_message_embed(ctx, "You must be verified over 18 years to use this command.", "Private")
            return  
        await self.bot.db.execute(f"UPDATE member SET birthday_greeting_public = FALSE WHERE guild_id = $1 AND member_id = $2", ctx.guild.id, ctx.author.id)
        await self.bot.output.show_message_embed(ctx, f"Your birthday greeting has been set to be private.", "Private")        


    # send_messages command
    @birthday_group.command(
        name="send_messages",
        hidden=True
    )
    async def send_messages_command(self, ctx):     
        if not await self.bot.roles.check_botmaster(ctx):
            return
        await self.utils.show_messages(ctx, ctx.guild.id)


def setup(bot):
    bot.add_cog(Birthdays(bot))    