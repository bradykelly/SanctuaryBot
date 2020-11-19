import time
import discord
import sanctuarybot.common
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from sanctuarybot import common
from sanctuarybot.db import db
from sanctuarybot.config import Config

class Bot(commands.Bot):

    def __init__(self, version, intents):
        self.version = version
        self._cogs = [p.stem for p in Path(".").glob("sanctuarybot/bot/cogs/*.py")]
        self._dynamic = "./sanctuarybot/data/dynamic"
        self._static = "./sanctuarybot/data/static"
        self.scheduler = AsyncIOScheduler()
        self.db = db.Database(self)

        super().__init__(command_prefix=self.command_prefix, case_insensitive=True, status=discord.Status.online, intents=intents)

    def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            try:
                self.load_extension(f"sanctuarybot.bot.cogs.{cog}")
            except Exception as ex:
                print(f"Error loading {cog}: {str(ex.args)}")
            else:
                print(f"Loaded {cog}.")
    
    def run(self):
        self.setup()

        print("Running bot...")
        super().run(Config.TOKEN, reconnect=True)

    async def shutdown(self):
        print("Shutting down...")
        self.scheduler.shutdown()
        print(" Shut down scheduler.")
        
        #TODO Are we using a hub, or where must this message go?
        # hub = self.get_cog("Hub")
        # if (sc := getattr(hub, "stdout_channel", None)) is not None:
        #     await sc.send(f"{self.info} {Config.BOT_NAME} is now shutting down. (Version {self.version})")