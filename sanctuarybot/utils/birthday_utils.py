from datetime import datetime
from typing import AsyncGenerator

from discord.ext.commands.errors import MissingRequiredArgument

class BirthdayUtils():

    def __init__(self, bot):
        self.bot = bot

    messages_busy = False

    async def show_messages(self):
        bdayRecs = await self.bot.db.records("SELECT member_id, date_of_birth FROM member \
            WHERE birthday_greeting_time IS NULL AND date_of_birth = $1", datetime.date.today())
        for rec in bdayRecs:
            member = self.bot.get_user(rec["member_id"])
            #TODO Public or private
            await member.send(embed=self.build_birthday_message())
            await self.bot.db.execute("UPDATE member SET birthday_greeting_time = $1 WHERE member_id = $2", datetime.datetime.now(), rec["member_id"])
        await self.bot.db.execute("UPDATE member SET birthday_greeting_time = null WHERE date(birthday_greeting_time) < $1", datetime.date.today())         

    async def messages_job(self):
        BirthdayUtils.messages_busy = True
        try:
            await self.show_messages()
        except Exception as ex:
            msg = ex.message if hasattr(ex, "message") else f"Type of error: {str(ex)}"
            print(f"Exception running messages job: {msg}")
            error_cog = self.bot.get_cog("Error")
            await error_cog.log_error(ex)
        finally:
            BirthdayUtils.messages_busy = False

    async def set_birthdate(self, ctx, user_id, dob):    
        try:
            await self.bot.db.execute("INSERT INTO member (member_id, date_of_birth) VALUES($1, $2) \
                ON CONFLICT (member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth, birthday_greeting_time = NULL", 
                user_id, dob)
            return True
        except AsyncGenerator.exceptions.PostgresError as ex:
            error_cog = self.bot.get_cog("Error")
            await error_cog.command_error(ctx, ex)
            return False    

    async def handle_error(self, ctx, error, error_msg=None):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")
        else:
            msg = error.message if isinstance(error, Exception) else f"Type of error: {str(error)}" 
            if error_msg is not None:               
                await ctx.send(error_msg + f": {msg}")   
            else:
                await ctx.send(f"An unhandled error occurred while executing your command: {msg}")         

    async def check_over_18(self, ctx):
        if not self.bot.roles.user_has_over_18(ctx.guild, ctx.author):
            await ctx.send(f"You must be 18 or over to use this command")
            return False
        return True       

    def build_birthday_message(self):
        self.bot.embed.build(
            title="Happy Birthday!", 
            description="The Sanctuary community wishes you a very happy birthday",
            url="http://sancturaybot.co.za/help?command=birthday",
            author_url="http://sancturaybot.co.za",
            image="file://D:/Personal/Python+Projects/SanctuaryBot/images/bday1.jpg"
        )               