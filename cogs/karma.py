import discord
from discord.ext import commands
from emoji import demojize

from core import check, rubbercog, utils
from core.config import config
from core.text import text
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
        if ctx.invoked_subcommand is None:
            await self.karma_stalk(ctx, member=ctx.author)

    @karma.command(name="stalk")
    async def karma_stalk(self, ctx, member: discord.Member):
        """See someone's karma"""
        k = repo_k.get_karma(member.id)
        # fmt: off
        embed = self.embed(
            ctx=ctx,
            description=text.fill(
                "karma", "stalk_user",
                user=self.sanitise(member.display_name, limit=32)
            ),
        )
        embed.add_field(
            name=text.get("karma", "stalk_karma"),
            value=f"**{k.karma.value}** ({k.karma.position}.)",
            inline=False,
        )
        embed.add_field(
            name=text.get("karma", "stalk_positive"),
            value=f"**{k.positive.value}** ({k.positive.position}.)",
        )
        embed.add_field(
            name=text.get("karma", "stalk_negative"),
            value=f"**{k.negative.value}** ({k.negative.position}.)",
        )
        # fmt:on
        await ctx.send(embed=embed)
        await utils.delete(ctx)

    @karma.command(name="emote", aliases=["emoji"])
    async def karma_emote(self, ctx, emote: str):
        """See emote's karma"""
        if not self._isUnicode(emote):
            try:
                emote_id = int(emote.split(":")[2][:-1])
                emote = await ctx.guild.fetch_emoji(emote_id)
            except (ValueError, IndexError):
                return await utils.send_help(ctx)
            except discord.NotFound:
                return await ctx.send(text.get("karma", "emote not found"))

        value = repo_k.emoji_value_raw(emote)
        if value is None:
            return await ctx.send(text.get("karma", "emote not voted"))

        await ctx.send(text.fill("karma", "emote", emote=str(emote), value=str(value)))

    @karma.command(name="emotes", aliases=["emojis"])
    async def karma_emotes(self, ctx):
        """See karma for all emotes"""
        emotes = await ctx.guild.fetch_emojis()
        content = []

        emotes_positive = self._getEmoteList(emotes, repo_k.getEmotesByValue(1))
        content.append(text.get("karma", "emotes_positive"))
        content += self._emoteListToMessage(emotes, emotes_positive)

        emotes_negative = self._getEmoteList(emotes, repo_k.getEmotesByValue(-1))
        content.append(text.get("karma", "emotes_negative"))
        content += self._emoteListToMessage(emotes, emotes_negative)

        for line in [x for x in content if len(x) > 0]:
            await ctx.send(line)

    @commands.check(check.is_mod)
    @karma.command(name="vote")
    async def karma_vote(self, ctx, emote: str = None):
        """Vote for emote's karma value"""
        pass

    @commands.check(check.is_mod)
    @karma.command(name="set")
    async def karma_set(self, ctx, emote: discord.Emoji, value: int):
        """Set karma value without public vote"""
        repo_k.set_emoji_value(emote, value)
        await ctx.send(f"value of {emote} is now {value}")

    @karma.command(name="message")
    async def karma_message(self, ctx, link: str):
        """Get karma for given message"""
        pass

    @commands.check(check.is_mod)
    @karma.command(name="give")
    async def karma_give(self, ctx, member: discord.Member, value: int):
        """Give karma points to someone"""
        repo_k.update_karma(member=member, giver=ctx.author, emoji_value=value)
        success = "give success given" if value > 0 else "give success taken"
        await ctx.send(text.get("karma", success))

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
    def _isUnicode(self, text):
        demojized = demojize(text)
        if demojized.count(":") != 2:
            return False
        if demojized.split(":")[2] != "":
            return False
        return demojized != text

    def _getEmoteList(self, emotes: list, value: int) -> list:
        db_emotes = repo_k.getEmotesByValue(value)
        result = []

        # parse
        for emote_id in db_emotes:
            try:
                emote = discord.utils.get(emotes, id=int(emote_id))
                if emote is None:
                    # removed
                    repo_k.remove_emoji(emote_id)
                    continue
                result.append(emote)
            except ValueError:
                # emoji
                result.append(emote_id)

        return result

    def _emoteListToMessage(self, emotes: list, width: int) -> list:
        line = ""
        result = []
        for i, emote in enumerate(emotes):
            if i % 10 == 0:
                result.append(line)
                line = ""
            line += f"{emote} "
        result.append(line)

        return [r for r in result if len(r) > 0]

    ##
    ## Logic
    ##

    ##
    ## Errors
    ##


def setup(bot):
    bot.add_cog(Karma(bot))
