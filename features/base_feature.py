from discord.ext.commands import Bot

from core import config

class BaseFeature:
    def __init__(self, bot: Bot):
        self.bot = bot
