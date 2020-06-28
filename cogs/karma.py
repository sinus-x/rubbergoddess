import asyncio

import discord
from discord.ext import commands
from emoji import demojize

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository import karma_repo, subject_repo

repo_k = karma_repo.KarmaRepository()
repo_s = subject_repo.SubjectRepository()


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

    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
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

    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="emote", aliases=["emoji"])
    async def karma_emote(self, ctx, emote: str):
        """See emote's karma"""
        if not self._isUnicode(emote):
            try:
                emote_id = int(self._emoteToID(emote))
                emote = await ctx.guild.fetch_emoji(emote_id)
            except (ValueError, IndexError):
                return await utils.send_help(ctx)
            except discord.NotFound:
                return await ctx.send(text.get("karma", "emote not found"))

        value = repo_k.emoji_value_raw(emote)
        if value is None:
            return await ctx.send(text.get("karma", "emote not voted"))

        await ctx.send(text.fill("karma", "emote", emote=str(emote), value=str(value)))

    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="emotes", aliases=["emojis"])
    async def karma_emotes(self, ctx):
        """See karma for all emotes"""
        emotes = await ctx.guild.fetch_emojis()
        content = []

        emotes_positive = self._getEmoteList(emotes, "1")
        if len(emotes_positive) > 0:
            content.append(text.get("karma", "emotes_positive"))
            content += self._emoteListToMessage(emotes_positive, 10)

        emotes_negative = self._getEmoteList(emotes, "-1")
        if len(emotes_negative) > 0:
            content.append(text.get("karma", "emotes_negative"))
            content += self._emoteListToMessage(emotes_negative, 10)

        emotes_nonvoted = self._getNonvotedEmoteList(emotes)
        if len(emotes_nonvoted) > 0:
            content.append(text.get("karma", "emotes_nonvoted"))
            content += self._emoteListToMessage(emotes_nonvoted, 10)

        if len(content) == 0:
            content.append(text.get("karma", "no emotes"))

        for line in [x for x in content if (x and len(x) > 0)]:
            await ctx.send(line)

    @commands.check(check.is_mod)
    @karma.command(name="vote")
    async def karma_vote(self, ctx, emote: str):
        """Vote for emote's karma value"""
        await utils.delete(ctx)

        message = await ctx.send(
            text.fill(
                "karma",
                "vote info",
                emote=emote,
                time=config.get("karma", "vote time"),
                limit=config.get("karma", "vote limit"),
            )
        )
        await message.add_reaction("☑️")
        await message.add_reaction("0⃣")
        await message.add_reaction("❎")

        await asyncio.sleep(config.get("karma", "vote time") * 60)

        # update cached message
        message = await ctx.channel.fetch_message(message.id)

        positive = 0
        negative = 0
        neutral = 0
        for reaction in message.reactions:
            if reaction.emoji == "☑️":
                positive = reaction.count - 1
            elif reaction.emoji == "❎":
                negative = reaction.count - 1
            elif reaction.emoji == "0⃣":
                neutral = reaction.count - 1

        if positive + negative + neutral < config.get("karma", "vote limit"):
            return await ctx.send(text.fill("karma", "vote failed", emote=emote))

        result = 0
        if positive > negative + neutral:
            result = 1
        elif negative > positive + neutral:
            result = -1

        repo_k.set_emoji_value(str(self._emoteToID(emote)), result)
        await ctx.send(text.fill("karma", "vote result", emote=emote, value=result))

    @commands.check(check.is_mod)
    @karma.command(name="set")
    async def karma_set(self, ctx, emote: discord.Emoji, value: int):
        """Set karma value without public vote"""
        repo_k.set_emoji_value(str(self._emoteToID(emote)), value)
        await ctx.send(text.fill("karma", "emote", emote=emote, value=value))

    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="message")
    async def karma_message(self, ctx, link: str):
        """Get karma for given message"""
        converter = commands.MessageConverter()
        try:
            message = await converter.convert(ctx=ctx, argument=link)
        except Exception as error:
            return await self.output.error(ctx, "Message not found", error)

        # TODO Add timestamp in local timezone, message.created_at is at UTC
        embed = self.embed(ctx=ctx, description=f"{message.author}")

        # fmt: off
        count = True
        if message.channel.id in config.get("karma", "banned channels") \
        or (
            not config.get("karma", "count subjects")
            and repo_s.get(message.channel.name) is not None
        ):
            count = False
        for word in config.get("karma", "banned words"):
            if word in message.content:
                count = False
                break
        # fmt: on

        output = {"negative": [], "neutral": [], "positive": []}
        karma = 0

        for reaction in message.reactions:
            emote = reaction.emoji
            value = repo_k.emoji_value_raw(emote)
            if value == 1:
                output["positive"].append(emote)
                karma += reaction.count
                async for user in reaction.users():
                    if user.id == message.author.id:
                        karma -= 1
                        break
            elif value == -1:
                output["negative"].append(emote)
                karma -= reaction.count
                async for user in reaction.users():
                    if user.id == message.author.id:
                        karma += 1
                        break
            else:
                output["neutral"].append(emote)

        embed.add_field(name="Link", value=message.jump_url, inline=False)

        if count:
            for key, value in output.items():
                if len(value) == 0:
                    continue
                emotes = " ".join(str(emote) for emote in value)
                embed.add_field(name=text.get("karma", "embed_" + key), value=emotes)
            # fmt: off
            embed.add_field(
                name=text.get("karma", "embed_total"),
                value=f"**{karma}**",
                inline=False,
            )
            # fmt: on
        else:
            embed.add_field(name="\u200b", value=text.get("karma", "embed_disabled"), inline=False)
        await ctx.send(embed=embed)

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

    def _getEmoteList(self, guild_emotes: list, value: int) -> list:
        db_emotes = repo_k.getEmotesByValue(value)

        result = []
        for guild_emote in guild_emotes:
            if str(guild_emote.id) in db_emotes:
                result.append(guild_emote)
        return result

    def _getNonvotedEmoteList(self, guild_emotes: list) -> list:
        db_emotes = [x.emoji_ID for x in repo_k.get_all_emojis()]

        result = []
        for guild_emote in guild_emotes:
            if str(guild_emote.id) not in db_emotes:
                result.append(guild_emote)
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

    def _emoteToID(self, emote: str):
        if ":" in str(emote):
            return int(str(emote).split(":")[2][:-1])
        return emote

    ##
    ## Logic
    ##

    ##
    ## Errors
    ##


def setup(bot):
    bot.add_cog(Karma(bot))
