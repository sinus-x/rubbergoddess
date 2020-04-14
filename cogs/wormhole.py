import discord
from discord.ext import commands

from core import rubbergod
from config.config import config

class Wormhole (rubbergod.Rubbergod):
    """Allow sending messages between two servers"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False
        self.warp_orange = self.bot.get_channel(config.wormhole_source_channel)
        self.warp_blue = self.bot.get_channel(config.wormhole_target_channel)

    @commands.Cog.listener()
    async def on_message (self, message):
        if message.author == self.bot.user:
            return

        if message.channel == self.warp_blue:
            await self.warp_orange.send(discord.utils.escape_mentions(message.content))
        elif message.channel == self.warp_orange:
            await self.warp_blue.send(discord.utils.escape_mentions("> " + message.content))

def setup(bot):
    bot.add_cog(Wormhole(bot))

