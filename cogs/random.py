import random

import discord
from discord.ext import commands

from core import rubbercog, utils
from core.text import text


class Random(rubbercog.Rubbercog):
    """Pick, flip, roll dice"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def pick(self, ctx, *args):
        """"Pick an option"""
        option = self.sanitise(random.choice(args), limit=50)
        if option is not None:
            await ctx.send(text.fill("random", "answer", mention=ctx.author.mention, option=option))

        await utils.room_check(ctx)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def flip(self, ctx):
        """Yes/No"""
        option = random.choice(text.get("random", "flip"))
        await ctx.send(text.fill("random", "answer", mention=ctx.author.mention, option=option))

        await utils.room_check(ctx)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def random(self, ctx, first: int, second: int = None):
        """Pick number from interval"""
        if second is None:
            second = 0

        if first > second:
            first, second = second, first

        option = str(random.randint(first, second))
        await ctx.send(text.fill("random", "answer", mention=ctx.author.mention, option=option))

        await utils.room_check(ctx)


def setup(bot):
    bot.add_cog(Random(bot))
