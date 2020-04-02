import discord
from discord.ext import commands

from config import config

config = config.Config


class Wormhole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sibling = None
        self.sibling_id = config.wormhole_sibling_id
        self.wormhole = self.bot.get_channel(config.wormhole_channel_id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.sibling is None:
            self.sibling = await self.bot.fetch_user(self.sibling_id)

        if message.channel == self.wormhole and not message.author.bot:
            self.sibling.send(discord.utils.escape_mentions(message.content))
        elif (isinstance(message.channel, discord.DMChannel) and
              message.channel.recipient == self.sibling):
            self.wormhole.send(message.content)

def setup(bot):
    bot.add_cog(Wormhole(bot))
