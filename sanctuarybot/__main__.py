import discord
from sanctuarybot import config
from sanctuarybot.bot.bot import Bot


# TODO Figure out intents really needed and not just defaults.
#intents = discord.Intents(guilds=True, members=True, invites=True, presences=True, messages=True, reactions=True)
intents = discord.Intents.all()

def main():
    bot = Bot(config.BOT_VERSION, intents=intents)
    bot.run()

if __name__ == '__main__':
    main()