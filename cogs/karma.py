import asyncio

import discord
from discord.ext import commands
from emoji import demojize

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository import karma_repo, subject_repo
from repository.database.karma import Karma as DB_Karma

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
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @commands.command(aliases=["karmaboard"])
    async def leaderboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.sendBoard(ctx, "desc", offset)

    @commands.check(check.is_verified)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @commands.command(aliases=["ishaboard"])
    async def looserboard(self, ctx, offset: int = 0):
        """Karma leaderboard, from the least"""
        await self.sendBoard(ctx, "asc", offset)

    @commands.check(check.is_verified)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @commands.command()
    async def givingboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.sendBoard(ctx, "give", offset)

    @commands.check(check.is_verified)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @commands.command(aliases=["stealingboard"])
    async def takingboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.sendBoard(ctx, "take", offset)

    ##
    ## Listeners
    ##
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Karma add"""
        parsed_payload = await self._payloadToReaction(payload)
        if parsed_payload is None:
            return
        channel, member, message, emote = parsed_payload

        count = self.doCountKarma(member=member, message=message)
        if not count:
            return

        repo_k.karma_emoji(message.author, member, emote)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Karma remove"""
        parsed_payload = await self._payloadToReaction(payload)
        if parsed_payload is None:
            return
        channel, member, message, emote = parsed_payload

        count = self.doCountKarma(member=member, message=message)
        if not count:
            return

        repo_k.karma_emoji_remove(message.author, member, emote)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Scrolling, vote"""
        if user.bot:
            return

        if reaction.message.channel.id == config.get("channels", "vote"):
            await self.checkVoteEmote(reaction, user)

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

    async def _payloadToReaction(self, payload: discord.RawReactionActionEvent) -> tuple:
        """Return (channel, member, message, emote)"""
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            return

        member = channel.guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        if message is None:
            return

        if payload.emoji.is_custom_emoji():
            emote = payload.emoji.id
        else:
            emote = payload.emoji.name

        return channel, member, message, emote

    async def _remove_reaction(self, reaction, user):
        try:
            await reaction.remove(user)
        except:
            pass

    ##
    ## Logic
    ##
    def doCountKarma(self, *, member: discord.Member, message: discord.Message) -> bool:
        """Return True only if the message should be counted"""
        # do not count author's reactions
        if member.id == message.author.id:
            return False

        # only count master and slave guilds
        if message.guild.id not in (config.guild_id, config.slave_id):
            return False

        # do not count banned channels
        if message.channel.id in config.get("karma", "banned channels"):
            return False

        # do not count banned roles
        if config.get("karma", "banned roles") in map(lambda x: x.id, member.roles):
            return False

        # do not count banned strings
        for word in config.get("karma", "banned words"):
            if word in message.content:
                return False

        # optionally, do not count subject channels
        if not config.get("karma", "count subjects"):
            if repo_s.get(message.channel.name) is not None:
                return False

        return True

    async def sendBoard(self, ctx: commands.Context, parameter: str, offset: int):
        """Send karma board

        parameter: desc | asc | give | take
        """
        max_offset = repo_k.getMemberCount() - config.get("karma", "leaderboard limit")
        if offset < 0:
            offset = 0
        elif offset > max_offset:
            offset = max_offset

        # fmt: off
        title = "{title}  {ordering}".format(
            title=text.get("karma", "board_title"),
            ordering=text.get("karma", "board_" + parameter + "_t"),
        )
        # fmt: on
        description = text.get("karma", "board_" + parameter + "_d")
        embed = self.embed(ctx=ctx, title=title, description=description)
        embed = self.fillBoard(embed, member=ctx.author, order=parameter, offset=offset)
        await ctx.send(embed=embed)

    def fillBoard(self, embed, *, member, order: str, offset: int) -> discord.Embed:
        limit = config.get("karma", "leaderboard limit")
        # around = config.get("karma", "leaderboard around")
        template = "`{position:>2}` … `{karma:>5}` {username}"

        embed.clear_fields()

        # get repository parameters
        column = "karma"
        if order == "give":
            column = "positive"
        if order == "take":
            column == "negative"

        if order == "desc":
            attr = DB_Karma.karma.desc()
        elif order == "asc":
            attr = DB_Karma.karma
        elif order == "give":
            attr = DB_Karma.positive.desc()
        elif order == "take":
            attr = DB_Karma.negative.desc()

        # construct first field
        value = []
        board = repo_k.getLeaderboard(attr, offset, limit)

        for i, db_user in enumerate(board, start=offset):
            # fmt: off
            user = self.bot.get_user(int(db_user.discord_id))
            username = (
                self.sanitise(user.display_name)
                if hasattr(user, "display_name")
                else "_unknown_"
            )

            if int(db_user.discord_id) == member.id:
                username = f"**{username}**"

            value.append(template.format(
                position=i + 1,
                karma=getattr(db_user, column),
                username=username,
            ))
            # fmt: on

        if offset == 0:
            name = text.fill("karma", "board_1", num=limit)
        else:
            name = text.fill("karma", "board_x", num=limit, offset=offset + 1)
        embed.add_field(name=name, value="\n".join(value))

        # construct second field
        # FIXME How to get user's position?
        # value = []
        # board = repo_k.getLeaderboard(attr, offset=user_position - around, limit=around*2+1)

        return embed

    async def checkVoteEmote(self, reaction, user):
        """Check if the emote is vote emote"""
        if not hasattr(reaction, "emoji"):
            return await self._remove_reaction(reaction, user)

        if str(reaction.emoji) not in ("☑️", "0⃣", "❎"):
            await self._remove_reaction(reaction, user)

    ##
    ## Errors
    ##


def setup(bot):
    bot.add_cog(Karma(bot))
