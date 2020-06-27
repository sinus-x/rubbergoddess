import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from repository import karma_repo

repo_k = karma_repo.KarmaRepository()


class Karma(rubbercog.Rubbercog):
    """Karma"""

    def __init__(self, bot):
        super().__init__(bot)

    ##
    ## Commands
    ##
    @commands.check(check.is_verified)
    @commands.group(name="karma")
    async def karma(self, ctx):
        """Karma"""
        pass

    @karma.command(name="check")
    async def karma_stalk(self, ctx, member: discord.Member):
        """See someone's karma"""
        pass

    @karma.command(name="emote", aliases=["emoji"])
    async def karma_emote(self, ctx, emote: str):
        """See emote's karma"""
        pass

    @karma.command(name="emotes", aliases=["emojis"])
    async def karma_emotes(self, ctx):
        """See karma for all emotes"""
        pass

    @commands.check(check.is_mod)
    @karma.command(name="vote")
    async def karma_vote(self, ctx, emote: str):
        """Vote for emote's karma value"""
        pass

    @commands.check(check.is_mod)
    @karma.command(name="set")
    async def karma_set(self, ctx, emote: str):
        """Set karma value without public vote"""
        pass

    @karma.command(name="message")
    async def karma_message(self, ctx, link: str):
        """Get karma for given message"""
        pass

    @commands.check(check.is_mod)
    @karma.command(name="give")
    async def karma_give(self, ctx, member: discord.Member, value: int):
        """Give karma points to someone"""
        pass

    @commands.check(check.is_verified)
    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @commands.command(name="leaderboard", aliases=["karmaboard", "userboard"])
    async def leaderboard(self, ctx, parameter: str = "desc"):
        """Karma leaderboard

        parameter: [desc (default) | asc | give | take]
        """
        pass

    ##
    ## Listeners
    ##
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Karma add"""
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Karma remove"""
        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Scrolling"""
        pass

    ##
    ## Helper functions
    ##

    ##
    ## Logic
    ##

    ##
    ## Errors
    ##


def setup(bot):
    bot.add_cog(Karma(bot))
