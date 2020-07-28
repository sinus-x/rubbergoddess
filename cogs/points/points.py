import datetime
import random

import discord
from discord.ext import commands

from core import rubbercog, utils
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

        await utils.send(ctx, f"You have {result.points} points and hold {position}. position.")

    @points.command(name="leaderboard", aliases=["🏆"])
    async def points_leaderboard(self, ctx):
        """Points leaderboard"""
        embed = self.embed(ctx=ctx, title="MEE6 🏆")
        value = self._getBoard(ctx.author, repo_p.getUsers("desc"))
        embed.add_field(name="Top 10", value=value)
        await utils.send(ctx, embed=embed)

    @points.command(name="loserboard", aliases=["💩"])
    async def points_loserboard(self, ctx):
        """Points leaderboard, ascending"""
        embed = self.embed(ctx=ctx, title="MEE6 💩")
        value = self._getBoard(ctx.author, repo_p.getUsers("asc"))
        embed.add_field(name="Bottom 10", value=value)
        await utils.send(ctx, embed=embed)

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

    ##
    ## Helper functions
    ##

    def _getBoard(self, author: discord.Member, users: list) -> str:
        result = []
        template = "`{points:>8}` … {name}"
        for db_user in users:
            user = self.bot.get_user(db_user.user_id)
            if user and user.display_name:
                name = discord.utils.escape_markdown(user.display_name)
            else:
                name = "???"

            if db_user.user_id == author.id:
                name = "**" + name + "**"

            result.append(template.format(points=db_user.points, name=name))
        return "\n".join(result)


def setup(bot):
    bot.add_cog(Points(bot))
