import datetime
import random

import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository.points_repo import PointsRepository

repo_p = PointsRepository()


class Points(rubbercog.Rubbercog):
    """MEE6-like XP"""

    def __init__(self, bot):
        super().__init__(bot)

        self.stats = {}

    ##
    ## Commands
    ##

    @commands.group(name="points", aliases=["body"])
    async def points(self, ctx):
        """Points? Points!"""
        await utils.send_help(ctx)

    @points.command(name="get", aliases=["gde"])
    async def points_get(self, ctx, member: discord.Member = None):
        """Get user points"""
        if member is None:
            member = ctx.author

        result = repo_p.get(member.id)
        position = repo_p.getPosition(result.points)

        await ctx.send(f"You have {result.points} points and hold {position}. position.")

    @points.command(name="leaderboard")
    async def points_leaderboard(self, ctx):
        """Points leaderboard"""
        pass

    @points.command(name="loserboard")
    async def points_loserboard(self, ctx):
        """Points leaderboard, ascending"""
        pass

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        now = datetime.datetime.now()
        value = random.randint(15, 25)

        if (
            str(message.author.id) in self.stats
            and (now - self.stats[str(message.author.id)]).total_seconds() < 60
        ):
            return

        self.stats[str(message.author.id)] = now
        repo_p.increment(message.author.id, value)


def setup(bot):
    bot.add_cog(Points(bot))
