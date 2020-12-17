import discord
from sanctuarybot.db import Database

class Roles:
    def __init__(self, bot):
        self.bot = bot

    def get_role_by_name(self, guild, roleName):
        for role in guild.roles:
            if role.name.lower() == roleName.lower():
                return role
        return None

    async def get_over_18_roles(self):
        over18roles = {}
        roleRows = await self.bot.db.records("SELECT guild_id, over_18_role_names FROM guild")
        for row in roleRows:
            roleNames = row["over_18_role_names"].split(";") if row["over_18_role_names"] is not None else []
            guild = self.bot.get_guild(row["guild_id"])
            over18roles[guild.name] = [self.get_role_by_name(guild, name) for name in roleNames]
        return over18roles

    async def get_botmaster_roles(self):
        botMasterRoles = {}
        roleRows = await self.bot.db.records("SELECT guild_id, botmaster_role_names FROM guild")
        for row in roleRows:
            roleNames = row["botmaster_role_names"].split(";") if row["botmaster_role_names"] is not None else []
            guild = self.bot.get_guild(row["guild_id"])
            botMasterRoles[guild.name] = [self.get_role_by_name(guild, name) for name in roleNames]
        return botMasterRoles