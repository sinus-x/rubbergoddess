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
        if msgbl.command is not None:
            result += f" (`{config.prefix}{msgbl.command.qualified_name}`)"
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

    async def debug(self, msg):
        if self.level <= logging.DEBUG:
            print(f"{getTimestamp()} DEB: {msg}")

    async def info(self, msg):
        if self.level <= logging.INFO:
            print(f"{getTimestamp()} INF: {msg}")

    async def warning(self, msg):
        if self.level <= logging.WARNING:
            print(f"{getTimestamp()} WAR: {msg}")

    async def error(self, msg):
        if self.level <= logging.ERROR:
            print(f"{getTimestamp()} ERR: {msg}")

    async def critical(self, msg):
        if self.level <= logging.CRITICAL:
            print(f"{getTimestamp()} CRT: {msg}")

