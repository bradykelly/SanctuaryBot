import time
import discord
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from sanctuarybot.db import db
from sanctuarybot.config import Config
from sanctuarybot.utils.roles import Roles
from sanctuarybot.bot.ready import Ready
from sanctuarybot.utils.emoji import EmojiGetter
from sanctuarybot.utils.view import StringViewSpaces
from discord.ext.commands.context import Context
from sanctuarybot.utils.output import OutputUtils

class Bot(commands.Bot):

    def __init__(self, version, intents):
        self.version = version
        self._cogs = [p.stem for p in Path(".").glob("sanctuarybot/bot/cogs/*.py")]
        self._dynamic = "./sanctuarybot/data/dynamic"
        self._static = "./sanctuarybot/data/static"
        self.scheduler = AsyncIOScheduler()
        self.db = db.Database(self, Config.DSN)
        self.roles = Roles(self)
        self.output = OutputUtils(self)
        self.emoji = EmojiGetter(self)
        self.ready = Ready(self)

        #but if you really want you can use bot.loop.run_until_complete(func())

        super().__init__(command_prefix=self.command_prefix, case_insensitive=True, status=discord.Status.online, intents=intents)

    #TODO Prevent DM commands

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

    async def shutdown(self, channel):
        print("Shutting down...")
        self.scheduler.shutdown()
        print(" Shut down scheduler.")

        print(" Bot is shutting down.")
        await channel.send(f" {self.info} {Config.BOT_NAME} is now shutting down. (Version {self.version})")        

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
            prefix = await self.db.field("SELECT command_prefix FROM guild WHERE guild_id = $1", guild.id)
            if not prefix:
                return Config.DEFAULT_PREFIX
            return prefix.strip()

    async def command_prefix(self, bot, msg):
        prefix = await self.prefix(msg.guild)
        return commands.when_mentioned_or(prefix or Config.DEFAULT_PREFIX)(bot, msg) 

    async def get_context(self, message, *, cls=Context):
        view = StringViewSpaces(message.content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)

        if self._skip_check(message.author.id, self.user.id):
            return ctx

        prefix = await self.get_prefix(message)
        invoked_prefix = prefix

        if isinstance(prefix, str):
            if not view.skip_string(prefix):
                return ctx
        else:
            try:
                # if the context class' __init__ consumes something from the view this
                # will be wrong.  That seems unreasonable though.
                if message.content.startswith(tuple(prefix)):
                    invoked_prefix = discord.utils.find(view.skip_string, prefix)
                else:
                    return ctx

            except TypeError:
                if not isinstance(prefix, list):
                    raise TypeError("get_prefix must return either a string or a list of string, "
                                    "not {}".format(prefix.__class__.__name__))

                # It's possible a bad command_prefix got us here.
                for value in prefix:
                    if not isinstance(value, str):
                        raise TypeError("Iterable command_prefix or list returned from get_prefix must "
                                        "contain only strings, not {}".format(value.__class__.__name__))

                # Getting here shouldn't happen
                raise

        invoker = view.get_word().strip()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        ctx.command = self.all_commands.get(invoker)
        return ctx

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            if isinstance(msg.channel, discord.DMChannel):
                await ctx.send(f"{self.cross} {Config.BOT_NAME} does not support command invokations in DMs.")
            elif not self.ready.booted:
                await ctx.send(
                    f"{self.cross} {Config.BOT_NAME} is still booting and is not ready to receive commands. Please try again later."
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


        