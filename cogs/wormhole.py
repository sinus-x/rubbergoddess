import discord
from discord.ext import commands

from config.config import Config as config

class Wormhole(commands.Cog):
    """A wormhole for crossposting between two servers"""
    def __init__(self, bot):
        self.bot = bot
        self.sibling = self.bot.get_user(config.wormhole_sibling_id)
        self.wormhole = self.bot.get_channel(config.wormhole_channel_id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.wormhole and not message.author.bot:
            self.sibling.send(discord.utils.escape_mentions(message.content))
        elif (isinstance(message.channel, discord.DMChannel) and
              message.channel.recipient == self.sibling):
            self.wormhole.send(message.content)

def setup(bot):
    bot.add_cog(Wormhole(bot))
