import logging
from datetime import datetime

import discord

from core.config import config

def getTimestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Output:
    def __init__(self, bot: discord.ext.commands.Bot = None):
        self.bot = bot
        self.level = getattr(logging, config.get('bot', 'logging').upper())

    def bot(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    async def debug(self, msgbl: discord.abc.Messageable, msg: str):
        if self.level <= logging.DEBUG:
            await self.send(msgbl, "Debug", msg, delete_after=config.get('delay', 'embed'))

    async def info(self, msgbl: discord.abc.Messageable, msg: str):
        if self.level <= logging.INFO:
            await self.send(msgbl, "Info", msg, delete_after=config.get('delay', 'embed'))

    async def warning(self, msgbl: discord.abc.Messageable, msg: str):
        if self.level <= logging.WARNING:
            await self.send(msgbl, "Warning", msg, delete_after=config.get('delay', 'embed'))

    async def error(self, msgbl: discord.abc.Messageable, msg: str, error = None):
        if self.level <= logging.ERROR:
            await self.send(msgbl, "Error", msg, error)

    async def critical(self, msgbl: discord.abc.Messageable, msg: str, error = None):
        if self.level <= logging.CRITICAL:
            await self.send(msgbl, "Critical error", msg, error)

    async def send(self, msgbl: discord.abc.Messageable, level: str, msg: str, error = None, delete_after = None):
        result = f">>> **{level}**"
        try:
            result += f" (`{config.prefix}{msgbl.command.qualified_name}`)"
        except:
            pass
        result += f":\n{discord.utils.escape_mentions(msg)}"

        if error is not None:
            tr = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            if len(tr) > 1000:
                tr = tr[-1000:]
            result += f"\n```{tr}```"

        result += f"\n_{getTimestamp()}_"

        await msgbl.send(result, delete_after=delete_after)

class Console:
    def __init__(self, bot: discord.ext.commands.Bot = None):
        self.bot = bot
        self.level = getattr(logging, config.get('bot', 'logging').upper())

    def bot(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    def debug(self, src, msg, error = None):
        """Send output to console

        src: commands.Command invoked from context or string
        """
        try:
            src = src.command.qualified_name
        except:
            src = str(src)
        if self.level <= logging.DEBUG:
            print(f"{getTimestamp()} DEB [{src}]: {msg}")
            self.printTraceback(error)

    def info(self, src, msg, error = None):
        """Send output to console

        src: commands.Command invoked from context or string
        """
        try:
            src = src.command.qualified_name
        except:
            src = str(src)
        if self.level <= logging.INFO:
            print(f"{getTimestamp()} INF [{src}]: {msg}")
            self.printTraceback(error)

    def warning(self, src, msg, error = None):
        """Send output to console

        src: commands.Command invoked from context or string
        """
        try:
            src = src.command.qualified_name
        except:
            src = str(src)
        if self.level <= logging.WARNING:
            print(f"{getTimestamp()} WAR [{src}]: {msg}")
            self.printTraceback(error)

    def error(self, src, msg, error = None):
        """Send output to console

        src: commands.Command invoked from context or string
        """
        try:
            src = src.command.qualified_name
        except:
            src = str(src)
        if self.level <= logging.ERROR:
            print(f"{getTimestamp()} ERR [{src}]: {msg}")
            self.printTraceback(error)

    def critical(self, src, msg, error = None):
        """Send output to console

        src: commands.Command invoked from context or string
        """
        try:
            src = src.command.qualified_name
        except:
            src = str(src)
        if self.level <= logging.CRITICAL:
            print(f"{getTimestamp()} CRI [{src}]: {msg}")
            self.printTraceback(error)

    def printTraceback(self, error):
        if error is not None:
            tr = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            print(tr)
