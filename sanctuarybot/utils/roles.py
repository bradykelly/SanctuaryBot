import discord
from sanctuarybot.db import Database

class Roles:
    def __init__(self, bot):
        self.bot = bot

    async def get_over_18_roles(self):
        over18roles = {}
        roleRows = await self.bot.db.records("SELECT guild_id, over_18_role_names FROM guild_config")
        for row in roleRows:
            roleNames = row["over_18_role_names"]
            over18roles[row["guild_id"]] = roleNames.split(";") if roleNames else []
        return over18roles

    async def get_botmaster_roles(self):
        botMasterRoles = {}
        roleRows = await self.bot.db.records("SELECT guild_id, botmaster_role_names FROM guild_config")
        for row in roleRows:
            roleNames = row["botmaster_role_names"]
            botMasterRoles[row["guild_id"]] = roleNames.split(";") if roleNames else []
        return botMasterRoles