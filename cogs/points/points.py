import datetime
import random
from typing import Union

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import rubbercog, utils
from repository.points_repo import PointsRepository

repo_p = PointsRepository()

# TODO Add timer: iterate over stats every X minutes and remove everyone
#      with time expired


class Points(rubbercog.Rubbercog):
    """Get points by having conversations"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("points")
        self.text = CogText("points")

        self.limits = self.config.get("points")
        self.timeslot = self.config.get("timer")

        self.stats = {}

    ##
    ## Commands
    ##

    @commands.group(name="points", aliases=["body"])
    async def points(self, ctx):
        """Points? Points!"""
        await utils.send_help(ctx)

    @points.command(name="get", aliases=["gde", "me", "stalk"])
    async def points_get(self, ctx, member: discord.Member = None):
        """Get user points"""
        if member is None:
            member = ctx.author

        result = repo_p.get(member.id)
        position = repo_p.getPosition(result.points)

        if member.id == ctx.author.id:
            text = self.text.get("me", points=result, position=position)
        else:
            text = self.text.get(
                "stalk",
                display_name=self.sanitise(member.display_name),
                points=result,
                position=position,
            )

        await ctx.send(text)
        await utils.room_check(ctx)

    @points.command(name="leaderboard", aliases=["🏆"])
    async def points_leaderboard(self, ctx):
        """Points leaderboard"""
        embed = self.embed(
            ctx=ctx,
            title=self.text.get("embed", "title") + self.text.get("embed", "desc_suffix"),
            description=self.text.get("embed", "desc_description"),
        )
        value = self._getBoard(
            ctx.author, repo_p.getUsers("desc", limit=self.config.get("board"), offset=0)
        )
        embed.add_field(
            name=self.text.get("embed", "desc_0", num=self.config.get("board")), value=value
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("⏪")
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        await utils.room_check(ctx)

    @points.command(name="loserboard", aliases=["💩"])
    async def points_loserboard(self, ctx):
        """Points loserboard"""
        embed = self.embed(
            ctx=ctx,
            title=self.text.get("embed", "title") + self.text.get("embed", "asc_suffix"),
            description=self.text.get("embed", "asc_description"),
        )
        value = self._getBoard(
            ctx.author, repo_p.getUsers("asc", limit=self.config.get("board"), offset=0)
        )
        embed.add_field(
            name=self.text.get("embed", "asc_0", num=self.config.get("board")), value=value
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("⏪")
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        await utils.room_check(ctx)

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        """Add points on message"""
        if message.author.bot:
            return

        now = datetime.datetime.now()

        if (
            str(message.author.id) in self.stats
            and (now - self.stats[str(message.author.id)]).total_seconds() < self.timeslot
        ):
            return

        value = random.randint(self.limits[0], self.limits[1])
        self.stats[str(message.author.id)] = now
        repo_p.increment(message.author.id, value)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle board scrolling"""
        if user.bot:
            return

        if str(reaction) not in ("⏪", "◀", "▶"):
            return

        # fmt: off
        if len(reaction.message.embeds) != 1 \
        or type(reaction.message.embeds[0].title) != str \
        or not reaction.message.embeds[0].title.startswith(self.text.get("embed", "title")):
            return
        # fmt: on

        embed = reaction.message.embeds[0]

        # get ordering
        if embed.title.endswith(self.text.get("embed", "desc_suffix")):
            order = "desc"
        else:
            order = "asc"

        # get current offset
        if ", " in embed.fields[0].name:
            offset = int(embed.fields[0].name.split(" ")[-1]) - 1
        else:
            offset = 0

        # get new offset
        if str(reaction) == "⏪":
            offset = 0
        elif str(reaction) == "◀":
            offset -= self.config.get("board")
        elif str(reaction) == "▶":
            offset += self.config.get("board")

        if offset < 0:
            return await utils.remove_reaction(reaction, user)

        value = self._getBoard(
            user, repo_p.getUsers(order, limit=self.config.get("board"), offset=offset)
        )
        if not value:
            # offset too big
            return await utils.remove_reaction(reaction, user)

        if offset:
            name = self.text.get(
                "embed", order + "_n", num=self.config.get("board"), offset=offset + 1
            )
        else:
            name = self.text.get("embed", order + "_0", num=self.config.get("board"))
        embed.clear_fields()
        embed.add_field(name=name, value=value)

        await reaction.message.edit(embed=embed)
        await utils.remove_reaction(reaction, user)

    ##
    ## Helper functions
    ##

    def _getBoard(
        self, author: Union[discord.User, discord.Member], users: list, offset: int = 0
    ) -> str:
        result = []
        template = "`{points:>8}` … {name}"
        for db_user in users:
            user = self.bot.get_user(db_user.user_id)
            if user and user.display_name:
                name = discord.utils.escape_markdown(user.display_name)
            else:
                name = self.text.get("unknown")

            if db_user.user_id == author.id:
                name = "**" + name + "**"

            result.append(template.format(points=db_user.points, name=name))
        return "\n".join(result)
