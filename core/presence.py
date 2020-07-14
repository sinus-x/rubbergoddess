import datetime

import discord

from core.config import config
from core import utils


class Presence:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

        # fmt: off
        self.activity = discord.Game(
            start=datetime.datetime.utcnow(),
            name=config.prefix + "help | " + utils.git_hash()[:7],
        )
        # fmt: on

    async def set_presence(self):
        await self.bot.change_presence(activity=self.activity)
