import datetime as dt
from sanctuarybot.config import Config
import discord
import asyncpg
from datetime import datetime
from traceback import format_exc
from sanctuarybot import common
from discord.ext import commands
from sanctuarybot.utils import chron, string
from sanctuarybot.bot.basecog import BaseCog

#TODO Use as_codeblock for output

class Error(BaseCog):
    """Error handling and logging"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)

    async def error(self, err, *args, **kwargs):
        ref = await self.log_error(err)

        if err == "on_command_error":
            prefix = await self.bot.prefix(args[0].guild)
            await self.bot.output.show_message_embed(args[0],
                f"{self.bot.cross} Something went wrong (ref: {ref}). Quote this reference in the support server, which you can get a link for by using `{prefix}support`."
            )
        if isinstance(err, Exception):
            raise err  

    async def command_error(self, ctx, exc):
        prefix = await self.bot.prefix(ctx.guild)

        if isinstance(exc, commands.CommandNotFound):
            await self.bot.output.show_message_embed(ctx, f"{self.bot.cross} Command `{exc.param.name}`is not known to {Config.BOT_NAME}")

        # Custom check failure handling.
        elif hasattr(exc, "msg"):
            await self.bot.output.show_message_embed(ctx, f"{self.bot.cross} {exc.msg}")

        elif isinstance(exc, commands.MissingRequiredArgument):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} No `{exc.param.name}` argument was passed, despite being required. Use `{prefix}help {ctx.command}` for more information."
            )

        elif isinstance(exc, commands.BadArgument):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} One or more arguments are invalid. Use `{prefix}help {ctx.command}` for more information."
            )

        elif isinstance(exc, commands.TooManyArguments):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} Too many arguments have been passed. Use `{prefix}help {ctx.command}` for more information.",
            )

        elif isinstance(exc, commands.MissingPermissions):
            mp = string.list_of([str(perm.replace("_", " ")).title() for perm in exc.missing_perms], sep="or")
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} You do not have the {mp} permission(s), which are required to use this command."
            )

        elif isinstance(exc, commands.BotMissingPermissions):
            mp = string.list_of([str(perm.replace("_", " ")).title() for perm in exc.missing_perms], sep="or")
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} {Config.BOT_NAME} does not have the {mp} permission(s), which are required to use this command."
            )

        elif isinstance(exc, commands.NotOwner):
            await ctx.send(f"{self.bot.cross} That command can only be used by the {common.BOT_NAME} owner.")

        elif isinstance(exc, commands.CommandOnCooldown):
            # Hooray for discord.py str() logic.
            cooldown_texts = {
                "BucketType.user": "{} You can not use that command for another {}.",
                "BucketType.guild": "{} That command can not be used in this server for another {}.",
                "BucketType.channel": "{} That command can not be used in this channel for another {}.",
                "BucketType.member": "{} You can not use that command in this server for another {}.",
                "BucketType.category": "{} That command can not be used in this category for another {}.",
            }
            await self.bot.output.show_message_embed(ctx, 
                cooldown_texts[str(exc.cooldown.type)].format(
                    self.bot.cross, chron.long_delta(dt.timedelta(seconds=exc.retry_after))
                )
            )

        elif isinstance(exc, commands.InvalidEndOfQuotedStringError):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} {Config.BOT_NAME} expected a space after the closing quote, but found a(n) `{exc.char}` instead."
            )

        elif isinstance(exc, commands.ExpectedClosingQuoteError):
            await self.bot.output.show_message_embed(ctx, f"{self.bot.cross} {Config.BOT_NAME} expected a closing quote character, but did not find one.")

        # Base errors.
        elif isinstance(exc, commands.UserInputError):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} There was an unhandled user input problem (probably argument passing error). Use `{prefix}help {ctx.command}` for more information."
            )

        elif isinstance(exc, commands.CheckFailure):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} There was an unhandled command check error (probably missing privileges). Use `{prefix}help {ctx.command}` for more information."
            )

        elif isinstance(exc, asyncpg.exceptions.PostgresError):
            await self.bot.output.show_message_embed(ctx, 
                f"{self.bot.cross} There was an unhandled database error while executing command `{prefix}{ctx.command}`. The error is: {exc.message}"
            )

        # Non-command errors.
        elif (original := getattr(exc, "original", None)) is not None:
            if isinstance(original, discord.HTTPException):
                await self.bot.output.show_message_embed(ctx, 
                    f"{self.bot.cross} An HTTP exception occurred ({original.status})\n```{original.text}```"
                )
            else:
                raise original        
        else:
            raise exc

    async def log_error(self, obj):
        obj = getattr(obj, "message", obj)
        if isinstance(obj, discord.Message):
            cause = f"{obj.content}\n{obj!r}"
        else:
            cause = f"{obj!r}" if obj is not None else "Unkown"

        ref = self.bot.generate_id()
        tb = format_exc()
        await self.bot.db.execute(
            "INSERT INTO error (ref, error_time, cause, traceback) VALUES ($1, $2, $3, $4)", ref, datetime.now(), cause, tb
        )
        return ref


def setup(bot):
    bot.add_cog(Error(bot))
