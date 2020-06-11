import logging
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from core.config import config


def getTimestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Output:
    """Present errors to the user

    This class is meant to provide feedback to the user.
    Use Console class to send the text to stdout/logging channel.
    """

    def __init__(self, bot: discord.ext.commands.Bot = None):
        self.bot = bot
        self.level = getattr(logging, config.get("bot", "logging").upper())

    def bot(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    async def debug(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.DEBUG:
            await self.send(source, "debug", message, error)

    async def info(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.INFO:
            await self.send(source, "info", message, error)

    async def warning(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.WARNING:
            await self.send(source, "warning", message, error)

    async def error(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.ERROR:
            await self.send(source, "error", message, error)

    async def critical(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.CRITICAL:
            await self.send(source, "critical", message, error)

    async def send(
        self,
        source: discord.abc.Messageable,
        level: str,
        message: str = None,
        error: Exception = None,
    ):
        template = ">>> **{level}**: {message}"
        template_cont = "\n{error} ```{traceback}```"

        # make sure there is something after the colon
        if message is None and error is None:
            message = "unspecified"

        result = template.format(level=level.upper(), message=message)

        # parse error
        if error is not None:
            tr = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if len(tr) > 1000:
                tr = tr[-999:] + "…"
            result += template_cont.format(error=error, traceback=tr)

        await source.send(result, delete_after=config.get("delay", "bot error"))


class Console:
    def __init__(self, bot: discord.ext.commands.Bot = None):
        self.bot = bot
        self.level = getattr(logging, config.get("bot", "logging").upper())
        self.log_channel = None

    def getLogChannel(self):
        if self.log_channel == 0:
            return

        if self.log_channel is None:
            log_channel_id = config.get("channels", "stdout")
            if log_channel_id == 0:
                self.log_channel = 0
                return
            self.log_channel = self.bot.get_channel(log_channel_id)
        return self.log_channel

    def bot(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    async def debug(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.DEBUG:
            await self.send(source, "debug", message, error)

    async def info(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.INFO:
            await self.send(source, "info", message, error)

    async def warning(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.WARNING:
            await self.send(source, "warning", message, error)

    async def error(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.ERROR:
            await self.send(source, "error", message, error)

    async def critical(self, source, message: str = None, error: Exception = None):
        if self.level <= logging.CRITICAL:
            await self.send(source, "critical", message, error)

    async def send(
        # fmt: off
        self,
        source,
        level: str,
        message: str = None,
        error: Exception = None,
        # fmt: on
    ):
        if self.getLogChannel() is None:
            return

        template = (
            "{timestamp} {level:>8} [{position}] {message}\n"
            "{author} in {location}\n"
            "{traceback}"
        )
        """
        position ... command or message that have triggered the error
        message  ... log event argument
        author   ... author behind the log event
        location ... physical location
        """

        location = str(source)
        author = "unknown author"
        position = "unknown position"
        message = message or ""
        error = error or ""

        # parse source
        if isinstance(source, commands.Context):
            if isinstance(source.channel, discord.TextChannel):
                location = f"{source.channel.guild}/{source.channel.name}"
            else:
                location = "DM"
            author = str(source.author)
            position = source.invoked_with

        elif isinstance(source, discord.Message):
            if isinstance(source.channel, discord.TextChannel):
                location = f"{source.channel.guild}/{source.channel.name}"
            else:
                location = "DM"
            author = str(source.author)
            position = message.content[:50]

        elif isinstance(source, commands.Cog):
            position = source.name

        elif isinstance(source, commands.Command):
            position = source.qualified_name

        # parse error
        if error is not None:
            tr = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if len(tr) > 1000:
                tr = tr[-999:] + "…"
        else:
            tr = ""

        result = template.format(
            timestamp=getTimestamp(),
            level=level,
            position=position,
            message=message,
            author=author,
            location=location,
            traceback=tr,
        )

        await self.getLogChannel().send(f"```{result}```")
        print(result)


class Event:
    def __init__(self, bot):
        self.bot = bot
        self.channel = None

        self.user_template = "{user} in {location}: {message}"
        self.sudo_template = "{user} in {location}: {message}"

    def getChannel(self):
        if self.channel is None:
            self.channel = self.bot.get_channel(config.get("channels", "events"))
        return self.channel

    async def user(self, member: discord.Member, location: discord.abc.Messageable, message: str):
        """Unprivileged events"""
        # fmt: off
        await self.getChannel().send(self.user_template.format(
            user=str(member),
            location=location.mention,
            message=message.replace("@", "@\u200b"),
        ))
        # fmt: on

    async def sudo(self, member: discord.Member, location: discord.abc.Messageable, message: str):
        """Privileged events"""
        # fmt: off
        await self.getChannel().send(self.sudo_template.format(
            user=str(member),
            location=location.mention,
            message=message.replace("@", "@\u200b"),
        ))
        # fmt: on
