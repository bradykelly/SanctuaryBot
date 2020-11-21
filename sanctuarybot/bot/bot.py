import time
import discord
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from sanctuarybot import common
from sanctuarybot.db import db
from sanctuarybot.config import Config
from sanctuarybot.utils.ready import Ready
from sanctuarybot.utils.emoji import EmojiGetter

class Bot(commands.Bot):

    def __init__(self, version, intents):
        self.version = version
        self._cogs = [p.stem for p in Path(".").glob("sanctuarybot/bot/cogs/*.py")]
        self._dynamic = "./sanctuarybot/data/dynamic"
        self._static = "./sanctuarybot/data/static"
        self.scheduler = AsyncIOScheduler()
        self.db = db.Database(self, Config.DSN)
        self.emoji = EmojiGetter(self)
        self.ready = Ready(self)

        super().__init__(command_prefix=self.command_prefix, case_insensitive=True, status=discord.Status.online, intents=intents)

    def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            try:
                self.load_extension(f"sanctuarybot.bot.cogs.{cog}")
            except Exception as ex:
                print(f"Error loading {cog} cog: {str(ex.args)}")
            else:
                print(f"Loaded {cog} cog.")
    
    def run(self):
        self.setup()

        print("Running bot...")
        super().run(Config.TOKEN, reconnect=True)

    async def shutdown(self):
        print("Shutting down...")
        self.scheduler.shutdown()
        print(" Shut down scheduler.")
        
        hub = self.get_cog("Hub")
        if (sc := getattr(hub, "stdout_channel", None)) is not None:
            await sc.send(f"{self.info} {Config.BOT_NAME} is now shutting down. (Version {self.version})")

        print(" Closing connection to Discord...")
        await self.logout()

    async def on_connect(self):
        if not self.ready.booted:
            print(f" Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def on_resumed(self):
        print("Bot resumed.")

    async def on_ready(self):
        if not self.ready.booted:
            print(" Readied.")
            self.client_id = (await self.application_info()).id

            self.scheduler.start()
            print(f" Scheduler started ({len(self.scheduler.get_jobs()):,} job(s)).")

            await self.db.sync()
            self.ready.synced = True
            print(" Synchronised database.")

            self.ready.booted = True
            print(" Bot booted. Don't use CTRL+C to shut the bot down!")     
        else:
            print("Bot reconnected.")    

    async def on_error(self, err, *args, **kwargs):
        error = self.get_cog("Error")
        await error.error(err, *args, **kwargs)

    async def on_command_error(self, ctx, exc):
        error = self.get_cog("Error")
        await error.command_error(ctx, exc)

    async def prefix(self, guild):
        if guild is not None:
            prefix = await self.db.field("SELECT command_prefix FROM guild_config WHERE guild_id = $1", guild.id)
            if not prefix:
                return Config.DEFAULT_PREFIX
            return prefix.strip()

    async def command_prefix(self, bot, msg):
        prefix = await self.prefix(msg.guild)
        return commands.when_mentioned_or(prefix or Config.DEFAULT_PREFIX)(bot, msg) 

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            if isinstance(msg.channel, discord.DMChannel):
                await ctx.send(f"{self.cross} {common.BOT_NAME} does not support command invokations in DMs.")
            elif not self.ready.booted:
                await ctx.send(
                    f"{self.cross} {common.BOT_NAME} is still booting and is not ready to receive commands. Please try again later."
                )
            else:
                await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)       

    @property
    def guild_count(self):
        return len(self.guilds)

    @property
    def user_count(self):
        return len(self.users)

    @property
    def command_count(self):
        return len(self.commands)

    @property
    def non_admin_invite(self):
        return discord.utils.oauth_url(
            self.client_id,
            permissions=discord.Permissions(
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                embed_links=True,
                read_message_history=True,
                use_external_emojis=True,
                add_reactions=True,
            ),
        )

    @property
    def tick(self):
        return self.emoji.mention("confirm")

    @property
    def cross(self):
        return self.emoji.mention("cancel")

    @property
    def info(self):
        return self.emoji.mention("info")

    @staticmethod
    def generate_id():
        return hex(int(time.time() * 1e7))[2:]


        