import discord
from sanctuarybot.db import Database

class Roles:
    def __init__(self, bot):
        self.bot = bot

    #TEST
    async def user_has_over_18(self, guild: discord.Guild, user: discord.User) -> bool:
        over18role = await self.bot.db.field("SELECT over_18_role_name \
            FROM guild_config WHERE guild_id = $1", guild.id)
        return over18role in user.roles

    #TEST
    async def user_has_botmaster(self, guild: discord.Guild, user: discord.User) -> bool:
        rolesList = await self.bot.db.field("SELECT botmaster_roles_list \
            FROM guild_config WHERE guild_id = $1", guild.id)
        botMasterRoles = rolesList.split(";")
        hasRole = False
        for role in botMasterRoles:
            if role in user.roles:
                hasRole = True
                break
        return hasRole