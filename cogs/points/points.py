import datetime
import random
from typing import Union

import discord
from discord.ext import commands, tasks

from cogs.resource import CogConfig, CogText
from core import rubbercog, utils
from repository.points_repo import PointsRepository

repo_p = PointsRepository()


class Points(rubbercog.Rubbercog):
    """Get points by having conversations"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("points")
        self.text = CogText("points")

        self.limits_message = self.config.get("points_message")
        self.timer_message = self.config.get("timer_message")
        self.limits_reaction = self.config.get("points_reaction")
        self.timer_reaction = self.config.get("timer_reaction")

        self.stats_message = {}
        self.stats_reaction = {}

        self.cleanup.start()

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
            text = self.text.get("me", points=result.points, position=position)
        else:
            text = self.text.get(
                "stalk",
                display_name=self.sanitise(member.display_name),
                points=result.points,
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
            str(message.author.id) in self.stats_message
            and (now - self.stats_message[str(message.author.id)]).total_seconds()
            < self.timer_message
        ):
            return

        value = random.randint(self.limits_message[0], self.limits_message[1])
        self.stats_message[str(message.author.id)] = now
        repo_p.increment(message.author.id, value)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle board scrolling"""
        if user.bot:
            return

        # add points
        now = datetime.datetime.now()
        if (
            str(user.id) not in self.stats_reaction
            or (now - self.stats_reaction[str(user.id)]).total_seconds() >= self.timer_reaction
        ):
            value = random.randint(self.limits_reaction[0], self.limits_reaction[1])
            self.stats_reaction[str(user.id)] = now
            repo_p.increment(user.id, value)

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

    ##
    ## Tasks
    ##

    @tasks.loop(seconds=120.0)
    async def cleanup(self):
        delete = []
        for uid, time in self.stats_message.items():
            if (datetime.datetime.now() - time).total_seconds() >= self.timer_message:
                delete.append(uid)
        for uid in delete:
            self.stats_message.pop(uid)
        delete = []
        for uid, time in self.stats_reaction.items():
            if (datetime.datetime.now() - time).total_seconds() >= self.timer_reaction:
                delete.append(uid)
        for uid in delete:
            self.stats_reaction.pop(uid)
