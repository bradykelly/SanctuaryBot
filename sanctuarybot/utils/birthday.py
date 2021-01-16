import discord
from datetime import datetime
from datetime import date

class BirthdayUtils():

    def __init__(self, bot):
        self.bot = bot

    show_messages_running = False

    async def show_messages(self, ctx=None, guild_id=None, forJob=False):
        if BirthdayUtils.show_messages_running:
            await self.bot.output.show_message_embed(ctx, "The show_messages job is busy running", "show_messages")
            return 
        BirthdayUtils.show_messages_running = True
        try:
            # Get all birthday members that haven't yet been greeted today.
            bdayRecs = await self.bot.db.records("SELECT member_id, date_of_birth, birthday_greeting_public FROM member \
                WHERE guild_id = $1 AND birthday_greeted_at IS NULL AND date_of_birth = $2", guild_id, date.today())

            channel = await self.get_birthday_channel(ctx)
            for rec in bdayRecs:
                user = self.bot.get_user(rec["member_id"])
                if not forJob and rec["birthday_greeting_public"] == True:                    
                    await channel.send(embed=self.build_birthday_message(user))
                else:
                    await user.send(embed=self.build_birthday_message(user))
                
                # Set the greeted date to prevent another greeting today.
                await self.bot.db.execute("UPDATE member SET birthday_greeted_at = $1 WHERE guild_id = $2 AND member_id = $3", datetime.now(), ctx.guild.id, rec["member_id"])

            # Clear all greeted dates before today. We will not greet them for another year.
            await self.bot.db.execute("UPDATE member SET birthday_greeted_at = NULL WHERE date(birthday_greeted_at) < $1", date.today())        
        finally:
            BirthdayUtils.show_messages_running = False

    async def messages_job(self):
        if BirthdayUtils.show_messages_running:
            return
        BirthdayUtils.show_messages_running = True
        try:
            for guild in self.bot.guilds:
                await self.show_messages(guild_id=guild.id, forJob=True)
        except Exception as ex:
            msg = ex.message if hasattr(ex, "message") else f"Error string: {str(ex)}"
            print(f"Exception running birthday messages job: {msg}")
            raise
        finally:
            BirthdayUtils.show_messages_running = False

    async def get_birthdate(self, ctx):
        dob = await self.bot.db.field("SELECT date_of_birth FROM member WHERE guild_id = $1 AND member_id = $2", ctx.guild.id, ctx.author.id)            
        return dob

    async def set_birthdate(self, ctx, user_id, dob):    
        await self.bot.db.execute("INSERT INTO member (guild_id, member_id, date_of_birth) VALUES($1, $2, $3) \
            ON CONFLICT (guild_id, member_id) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth, birthday_greeted_at = NULL", 
            ctx.guild.id, user_id, dob)

    async def get_birthday_channel(self, ctx):
        channelName = await self.bot.db.field("SELECT birthday_channel FROM guild WHERE guild_id = $1", ctx.guild.id)
        channel = discord.utils.get(ctx.guild.channels, name=channelName)
        return channel

    def build_birthday_message(self, user):
        embed = self.bot.embed.build(
            title=f"Happy Birthday!", 
            description=f"{user.mention}, the Sanctuary community wishes you a very happy birthday",
            url="http://sancturaybot.co.za/help?command=birthday",
            author_url="http://sancturaybot.co.za"
            #image="file://D:/Personal/Python+Projects/SanctuaryBot/images/bday1.jpg"
        )  
        return embed             