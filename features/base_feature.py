from discord.ext.commands import Bot


class BaseFeature:
    def __init__(self, bot: Bot):
        self.bot = bot
