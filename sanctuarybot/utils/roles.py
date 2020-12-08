import discord
from sanctuarybot.db import Database

class Roles:
    def __init__(self, bot):
        self.bot = bot

    async def user_has_over_18(self, guild: discord.Guild, user: discord.User) -> bool:
        over18role = await self.bot.db.field("SELECT over_18_role_name FROM guild_config \
            WHERE guild_id = $1", guild.id)
        user = self.bot.get_user(user.author.id)
        return over18role in user.roles