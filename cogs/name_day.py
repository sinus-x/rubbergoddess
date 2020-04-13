import requests

import discord
from discord.ext import commands

from core import rubbercog, utils
from config.config import config
from config.messages import Messages as messages


class Name_day(rubbercog.Rubbercog):
    """See today's nameday for czech and slovak calendars"""
    def __init__(self, bot):
        self.bot = bot
        self.visible = True

    @commands.command(aliases=["svátek"])
    async def svatek(self, ctx):
        url = config.nameday_cz
        res = requests.get(url).json()
        names = []
        for i in res:
            names.append(i["name"])
        await ctx.send(messages.name_day_cz.format(name=", ".join(names)))

    @commands.command()
    async def meniny(self, ctx):
        url = config.nameday_sk
        res = requests.get(url).json()
        names = []
        for i in res:
            names.append(i["name"])
        await ctx.send(messages.name_day_sk.format(name=", ".join(names)))


def setup(bot):
    bot.add_cog(Name_day(bot))
