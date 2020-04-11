import datetime

import discord
from discord.ext import commands

from core import rubbercog, utils
from config.config import config
from config.messages import Messages as messages


class Kachna(rubbercog.Rubbercog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kachna(self, ctx):
        await ctx.send(messages.kachna_grillbot)
        await self.deleteCommand(ctx)


def setup(bot):
    bot.add_cog(Kachna(bot))
