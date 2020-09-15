import logging
import traceback
from datetime import datetime
from typing import Union

import discord
from discord.ext import commands

from core.config import config
from core.text import text


def getTimestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# TODO Add own level so we do not need to use logging for just this


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

    async def debug(
        self,
        source: Union[commands.Context, discord.Message],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.DEBUG:
            await self.send(source, "debug", message, error)

    async def info(
        self,
        source: Union[commands.Context, discord.Message],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.INFO:
            await self.send(source, "info", message, error)

    async def warning(
        self,
        source: Union[commands.Context, discord.Message],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.WARNING:
            await self.send(source, "warning", message, error)

    async def error(
        self,
        source: Union[commands.Context, discord.Message],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.ERROR:
            await self.send(source, "error", message, error)

    async def critical(
        self,
        source: Union[commands.Context, discord.Message],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.CRITICAL:
            await self.send(source, "critical", message, error)

    async def send(
        self,
        source: Union[commands.Context, discord.Message],
        level: str,
        message: str = None,
        error: Exception = None,
    ):
        """Send output to source channel"""

        template = ">>> **{level}**: {message}"
        template_cont = "\n{error} ```{traceback}```"

        # make sure there is something after the colon
        if message is None and error is None:
            message = "unspecified"

        result = template.format(level=text.get("bot", level).upper(), message=message)

        # parse error
        if error is not None:
            tr = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if len(tr) > 1000:
                tr = "…" + tr[-999:]

            # escape
            error = discord.utils.escape_markdown(str(error)).replace("@", "@\u200b")
            tr = tr.replace("```", "`\u200b`\u200b`")

            result += template_cont.format(error=error, traceback=tr)

        if level in ("debug", "info", "warning"):
            await source.send(result, delete_after=config.get("delay", "bot error"))
        else:
            await source.send(result)


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

    async def debug(
        self,
        source: Union[commands.Context, discord.Message, str],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.DEBUG:
            await self.send(source, "debug", message, error)

    async def info(
        self,
        source: Union[commands.Context, discord.Message, str],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.INFO:
            await self.send(source, "info", message, error)

    async def warning(
        self,
        source: Union[commands.Context, discord.Message, str],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.WARNING:
            await self.send(source, "warning", message, error)

    async def error(
        self,
        source: Union[commands.Context, discord.Message, str],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.ERROR:
            await self.send(source, "error", message, error)

    async def critical(
        self,
        source: Union[commands.Context, discord.Message, str],
        message: str = None,
        error: Exception = None,
    ):
        if self.level <= logging.CRITICAL:
            await self.send(source, "critical", message, error)

    async def send(
        # fmt: off
        self,
        source: Union[commands.Context, discord.Message, str],
        level: str,
        message: str = None,
        error: Exception = None,
        # fmt: on
    ):
        if self.getLogChannel() is None:
            return

        template = "{timestamp} {level} [{command}] {message}\n{author}, {source_name}"

        # command
        if isinstance(source, commands.Context) and hasattr(source.command, "qualified_name"):
            command = source.command.qualified_name
        else:
            command = "not a command"

        # author
        if hasattr(source, "author") and type(source.author) in (discord.User, discord.Member):
            author = str(source.author)
        else:
            author = "unknown author"

        # source_name
        if hasattr(source, "channel") and isinstance(source.channel, discord.TextChannel):
            source_name = f"{source.channel.name} in {source.channel.guild}"
        elif hasattr(source, "channel"):
            source_name = type(source.channel).__name__
        else:
            source_name = "unknown location"

        # message
        if message is None and error is not None:
            message = str(error)
        elif message is None:
            message = "no message"

        # traceback
        if error and len(str(error.__traceback__)):
            tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        else:
            tb = ""

        result = template.format(
            timestamp=getTimestamp(),
            level=level.upper(),
            command=command,
            message=message,
            author=author,
            source_name=source_name,
        )
        if len(tb):
            result += "\n\n" + tb

        print(result)

        # send traceback
        result = list(result[0 + i : 1980 + i] for i in range(0, len(result), 1980))
        for r in result:
            await self.getLogChannel().send(f"```{r}```")

        # try to include trigger message
        content = None
        if isinstance(source, discord.Message):
            content = source.content
        elif isinstance(source, commands.Context):
            content = source.message.content
        if content is not None:
            await self.getLogChannel().send(f"Original:\n```{content[:1980]}```")


class Event:
    def __init__(self, bot):
        self.bot = bot
        self.channel = None

    def getChannel(self):
        if self.channel is None:
            self.channel = self.bot.get_channel(config.get("channels", "events"))
        return self.channel

    def _identifier(
        self, source: Union[commands.Context, discord.Message, discord.User, discord.Member, str]
    ):
        if hasattr(source, "channel"):
            # ctx, message
            if hasattr(source.channel, "mention"):
                # channel
                location = source.channel.mention
            else:
                # dm
                location = type(source.channel).__name__
            if hasattr(source, "author"):
                author = str(source.author)
            else:
                author = "unknown"
            identifier = f"{discord.utils.escape_markdown(author)} in {location}"
        elif isinstance(source, discord.User) or isinstance(source, discord.Member):
            # user or member
            identifier = str(source)
        else:
            # str
            identifier = source
        return discord.utils.escape_markdown(identifier)

    async def user(
        self,
        source: Union[commands.Context, discord.Message, discord.User, discord.Member, str],
        message: str,
        *,
        escape_markdown: bool = True,
    ):
        """Non-privileged events"""
        await self.getChannel().send(
            "**USER** "
            + self._identifier(source)
            + ": "
            + (message.replace("@", "@\u200b") if escape_markdown else message)
        )

    async def sudo(
        self,
        source: Union[commands.Context, discord.Message, discord.User, discord.Member, str],
        message: str,
        *,
        escape_markdown: bool = True,
    ):
        """Privileged events"""
        await self.getChannel().send(
            "**SUDO** "
            + self._identifier(source)
            + ": "
            + (message.replace("@", "@\u200b") if escape_markdown else message)
        )
