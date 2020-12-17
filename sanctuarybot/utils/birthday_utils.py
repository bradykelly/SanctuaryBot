from datetime import datetime
from discord.ext.commands.errors import MissingRequiredArgument

class BirthdayUtils():

    def __init__(self, bot):
        self.bot = bot

    messages_job_running = False

    async def show_messages(self, ctx):
        bdayRecs = await self.bot.db.records("SELECT member_id, date_of_birth FROM member \
            WHERE guild_id = $1 AND birthday_greeted_at IS NULL AND date_of_birth = $2", ctx.guild.id, datetime.date.today())
        for rec in bdayRecs:
            member = self.bot.get_user(rec["member_id"])
            #TODO Public or private
            await member.send(embed=self.build_birthday_message())
            await self.bot.db.execute("UPDATE member SET birthday_greeted_at = $1 WHERE guild_id = $2 AND member_id = $3", datetime.datetime.now(), ctx.guild.id, ctx.member.id, rec["member_id"])
        await self.bot.db.execute("UPDATE member SET birthday_greeted_at = null WHERE date(birthday_greeted_at) < $1", datetime.date.today())         

    async def messages_job(self):
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
        await self.bot.db.execute("INSERT INTO member (guild_id, member_id, date_of_birth) VALUES($1, $2, $3) \
            ON CONFLICT (guild_id, member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth, birthday_greeted_at = NULL", 
            ctx.guild.id, user_id, dob)

    def build_birthday_message(self):
        self.bot.embed.build(
            title="Happy Birthday!", 
            description="The Sanctuary community wishes you a very happy birthday",
            url="http://sancturaybot.co.za/help?command=birthday",
            author_url="http://sancturaybot.co.za",
            image="file://D:/Personal/Python+Projects/SanctuaryBot/images/bday1.jpg"
        )               