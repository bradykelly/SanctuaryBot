from datetime import datetime
from discord.ext.commands.errors import MissingRequiredArgument

class BirthdayUtils():

    def __init__(self, bot):
        self.bot = bot

    messages_job_running = False

    async def show_messages(self, forJob=False):
        bdayRecs = await self.bot.db.records("SELECT member_id, date_of_birth FROM member \
            WHERE birthday_greeting_time IS NULL AND date_of_birth = $1", datetime.date.today())
        for rec in bdayRecs:
            member = self.bot.get_user(rec["member_id"])
            #TODO Public or private
            await member.send(embed=self.build_birthday_message())
            await self.bot.db.execute("UPDATE member SET birthday_greeting_time = $1 WHERE member_id = $2", datetime.datetime.now(), rec["member_id"])
        await self.bot.db.execute("UPDATE member SET birthday_greeting_time = null WHERE date(birthday_greeting_time) < $1", datetime.date.today())         

    async def messages_job(self):
        if BirthdayUtils.messages_job_running:
            return
        BirthdayUtils.messages_job_running = True
        try:
            await self.show_messages(forJob=True)
        except Exception as ex:
            msg = ex.message if hasattr(ex, "message") else f"Error string: {str(ex)}"
            print(f"Exception running messages job: {msg}")
            raise
        finally:
            BirthdayUtils.messages_job_running = False

    async def set_birthdate(self, ctx, user_id, dob):    
        await self.bot.db.execute("INSERT INTO member (member_id, date_of_birth) VALUES($1, $2) \
            ON CONFLICT (member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth, birthday_greeting_time = NULL", 
            user_id, dob)

    def build_birthday_message(self):
        self.bot.embed.build(
            title="Happy Birthday!", 
            description="The Sanctuary community wishes you a very happy birthday",
            url="http://sancturaybot.co.za/help?command=birthday",
            author_url="http://sancturaybot.co.za",
            image="file://D:/Personal/Python+Projects/SanctuaryBot/images/bday1.jpg"
        )               