import discord
from sanctuarybot.db import Database

class Roles:
    def __init__(self, bot):
        self.bot = bot
        self.over18Roles = None
        self.botMasterRoles = None        

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

    async def check_over_18(self, ctx):
        if self.over18Roles is None:
            self.over18Roles = await self.get_over_18_roles()
        guildRoles = self.over18Roles[ctx.guild.name]
        hasRole = False
        for role in guildRoles:
            if role in ctx.author.roles:
                hasRole = True
                break
        if not hasRole:
            await self.bot.output.show_message_embed(ctx, "You must be verified over 18 years old to use this command.")
            return False
        else:
            return True        

    async def get_botmaster_roles(self):
        botMasterRoles = {}
        roleRows = await self.bot.db.records("SELECT guild_id, botmaster_role_names FROM guild")
        for row in roleRows:
            roleNames = row["botmaster_role_names"].split(";") if row["botmaster_role_names"] is not None else []
            guild = self.bot.get_guild(row["guild_id"])
            botMasterRoles[guild.name] = [self.get_role_by_name(guild, name) for name in roleNames]
        return botMasterRoles

    async def check_botmaster(self, ctx):
        if self.botMasterRoles is None:
            self.botMasterRoles = await self.get_botmaster_roles()
        guildRoles = self.botMasterRoles[ctx.guild.name]
        hasRole = False
        for role in guildRoles:
            if role in ctx.author.roles:
                hasRole = True
                break
        if not hasRole:
            await self.bot.output.show_message_embed(ctx, "You must have one of the BotMaster roles to use this command.")
            return False
        else:
            return True        