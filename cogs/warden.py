import discord
from discord.ext import commands

from core.config import config
from core.emote import emote
from core import check, rubbercog, utils

class Warden (rubbercog.Rubbercog):
    """A cog for database lookups"""
    def __init__ (self, bot):
        super().__init__(bot)
        self.visible = False

    # apt install libopenjp2-7 libtiff
    # pip3 install pillow dhash

    @commands.Cog.listener()
    async def on_message (self, message: discord.Message):
        if message.channel.id in config.get('warden cog', 'deduplication channels') \
        and message.files is not None:
            await self.checkDuplicate(message)


    async def checkDuplicate(self, message: discord.Message):
        """Check if uploaded files are known"""
        # get file hashes

        # try to search them directly

        # extract last 1000 items and iterate


    async def announceDuplicate(self, message: discord.Message, match: str):
        """Send message that a post is a duplicate

        match: [full|almost|possible]
        """



def setup(bot):
    bot.add_cog(Warden(bot))
