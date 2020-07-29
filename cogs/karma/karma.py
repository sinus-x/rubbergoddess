import asyncio
from typing import List

import discord
from discord.ext import commands
from emoji import demojize

from cogs.resource import CogConfig, CogText
from core import check, rubbercog, utils
from core.config import config
from repository import karma_repo, subject_repo
from repository.database.karma import Karma as DB_Karma

repo_k = karma_repo.KarmaRepository()
repo_s = subject_repo.SubjectRepository()


class Karma(rubbercog.Rubbercog):
    """Karma"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("karma")
        self.text = CogText("karma")

    ##
    ## Commands
    ##
    @commands.check(check.is_verified)
    @commands.group(name="karma")
    async def karma(self, ctx):
        """Karma"""
        await utils.delete(ctx)

        if ctx.invoked_subcommand is None:
            await self.karma_stalk(ctx, member=ctx.author)

    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="stalk")
    async def karma_stalk(self, ctx, member: discord.Member):
        """See someone's karma"""
        k = repo_k.get_karma(member.id)
        embed = self.embed(
            ctx=ctx,
            description=self.text.get("stalk_user", user=self.sanitise(member.display_name)),
        )
        embed.add_field(
            name=self.text.get("stalk_karma"),
            value=f"**{k.karma.value}** ({k.karma.position}.)",
            inline=False,
        )
        embed.add_field(
            name=self.text.get("stalk_positive"),
            value=f"**{k.positive.value}** ({k.positive.position}.)",
        )
        embed.add_field(
            name=self.text.get("stalk_negative"),
            value=f"**{k.negative.value}** ({k.negative.position}.)",
        )
        await ctx.send(embed=embed)
        await utils.room_check(ctx)

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
                return await ctx.send(self.text.get("emoji_not_found"))

        value = repo_k.emoji_value_raw(emote)
        if value is None:
            return await ctx.send(self.text.get("emoji_not_voted"))

        await ctx.send(self.text.get("emoji", emoji=str(emote), value=str(value)))
        await utils.room_check(ctx)

    @commands.guild_only()
    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="emotes", aliases=["emojis"])
    async def karma_emotes(self, ctx):
        """See karma for all emotes"""
        emotes = await ctx.guild.fetch_emojis()
        emotes = [e for e in emotes if not e.animated]
        content = []

        emotes_positive = self._getEmoteList(emotes, "1")
        if len(emotes_positive) > 0:
            content.append(self.text.get("emojis_positive"))
            content += self._emoteListToMessage(emotes_positive)

        emotes_neutral = self._getEmoteList(emotes, "0")
        if len(emotes_neutral) > 0:
            content.append(self.text.get("emojis_neutral"))
            content += self._emoteListToMessage(emotes_neutral)

        emotes_negative = self._getEmoteList(emotes, "-1")
        if len(emotes_negative) > 0:
            content.append(self.text.get("emojis_negative"))
            content += self._emoteListToMessage(emotes_negative)

        emotes_nonvoted = self._getNonvotedEmoteList(emotes)
        if len(emotes_nonvoted) > 0:
            content.append(self.text.get("emojis_nonvoted"))
            content += self._emoteListToMessage(emotes_nonvoted)

        if len(content) == 0:
            content.append(self.text.get("no_emojis"))

        line = ""
        for items in [x for x in content if (x and len(x) > 0)]:
            if items[0] != "<":
                # description
                if len(line):
                    await ctx.send(line)
                    line = ""
                await ctx.send(items)
                continue

            if len(line) + len(items) > 2000:
                await ctx.send(line)
                line = ""

            line += "\n" + items
        await ctx.send(line)

        await utils.room_check(ctx)

    @commands.guild_only()
    @commands.check(check.is_mod)
    @karma.command(name="vote")
    async def karma_vote(self, ctx, emote: str = None):
        """Vote for emote's karma value"""
        if emote is None:
            emojis = await ctx.guild.fetch_emojis()
            emojis = [e for e in emojis if not e.animated]
            nonvoted = self._getNonvotedEmoteList(emojis)

            if len(nonvoted) == 0:
                return await ctx.author.send(
                    self.text.get("all_emojis_voted", guild=ctx.guild.name)
                )
            emote = nonvoted[0]

        message = await ctx.send(
            self.text.get(
                "vote_info",
                emoji=emote,
                time=self.config.get("vote time"),
                limit=self.config.get("vote limit"),
            )
        )
        # set default of zero, so we can run the command multiple times
        repo_k.set_emoji_value(str(self._emoteToID(emote)), 0)

        # add options and vote
        await message.add_reaction("☑️")
        await message.add_reaction("0⃣")
        await message.add_reaction("❎")

        await self.event.sudo(ctx, f"Vote over value of {emote} started.")
        await asyncio.sleep(self.config.get("vote time") * 60)

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

        if positive + negative + neutral < self.config.get("vote limit"):
            await self.event.sudo(ctx, f"Vote for {emote} failed.")
            return await ctx.send(self.text.get("vote_failed", emoji=emote))

        result = 0
        if positive > negative + neutral:
            result = 1
        elif negative > positive + neutral:
            result = -1

        repo_k.set_emoji_value(str(self._emoteToID(emote)), result)
        await ctx.send(self.text.get("vote_result", emoji=emote, value=result))
        await self.event.sudo(ctx, f"{emote} karma value voted as {result}.")

    @commands.check(check.is_mod)
    @karma.command(name="set")
    async def karma_set(self, ctx, emoji: discord.Emoji, value: int):
        """Set karma value without public vote"""
        repo_k.set_emoji_value(str(self._emoteToID(emoji)), value)
        await ctx.send(self.text.get("emoji", emoji=emoji, value=value))
        await self.event.sudo(ctx, f"Karma of {emoji} set to {value}.")

    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="message")
    async def karma_message(self, ctx, link: str):
        """Get karma for given message"""
        converter = commands.MessageConverter()
        try:
            message = await converter.convert(ctx=ctx, argument=link)
        except Exception as error:
            return await self.output.error(ctx, "Message not found", error)

        embed = self.embed(ctx=ctx, description=f"{message.author}")

        # fmt: off
        count = True
        if message.channel.id in self.config.get("banned channels") \
        or (
            not self.config.get("count subjects")
            and repo_s.get(message.channel.name) is not None
        ):
            count = False
        for word in self.config.get("banned words"):
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
                embed.add_field(name=self.text.get("embed_" + key), value=emotes)
            # fmt: off
            embed.add_field(
                name=self.text.get("embed_total"),
                value=f"**{karma}**",
                inline=False,
            )
            # fmt: on
        else:
            embed.add_field(name="\u200b", value=self.text.get("embed_disabled"), inline=False)
        await ctx.send(embed=embed)

        await utils.room_check(ctx)

    @commands.check(check.is_mod)
    @karma.command(name="give")
    async def karma_give(self, ctx, member: discord.Member, value: int):
        """Give karma points to someone"""
        repo_k.update_karma(member=member, giver=ctx.author, emoji_value=value)
        await ctx.send(self.text.get("give", "given" if value > 0 else "taken"))
        await self.event.sudo(ctx, f"{member} got {value} karma points.")

    @commands.check(check.is_verified)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @commands.command(aliases=["karmaboard"])
    async def leaderboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.sendBoard(ctx, "desc", offset)

    @commands.check(check.is_verified)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @commands.command()
    async def loserboard(self, ctx, offset: int = 0):
        """Karma leaderboard, from the worst"""
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

        if str(reaction) in ("⏪", "◀", "▶"):
            await self.checkBoardEmoji(reaction, user)

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

    def _emoteListToMessage(self, emotes: list) -> List[str]:
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
        if message.channel.id in self.config.get("banned channels"):
            return False

        # do not count banned roles
        if self.config.get("banned roles") in map(lambda x: x.id, member.roles):
            return False

        # do not count banned strings
        for word in self.config.get("banned words"):
            if word in message.content:
                return False

        # optionally, do not count subject channels
        if not self.config.get("count subjects"):
            if repo_s.get(message.channel.name) is not None:
                return False

        return True

    async def sendBoard(self, ctx: commands.Context, parameter: str, offset: int):
        """Send karma board

        parameter: desc | asc | give | take
        """
        # convert offset to be zero-base
        offset -= 1

        max_offset = repo_k.getMemberCount() - self.config.get("leaderboard limit")
        if offset < 0:
            offset = 0
        elif offset > max_offset:
            offset = max_offset

        # fmt: off
        title = "{title}  {ordering}".format(
            title=self.text.get("board_title"),
            ordering=self.text.get("board_" + parameter + "_t"),
        )
        # fmt: on
        description = self.text.get("board_" + parameter + "_d")
        embed = self.embed(ctx=ctx, title=title, description=description)
        embed = self.fillBoard(embed, member=ctx.author, order=parameter, offset=offset)

        message = await ctx.send(embed=embed)
        await message.add_reaction("⏪")
        await message.add_reaction("◀")
        await message.add_reaction("▶")

        await utils.room_check(ctx)

    def fillBoard(self, embed, *, member, order: str, offset: int) -> discord.Embed:
        limit = self.config.get("leaderboard limit")
        # around = config.get("karma", "leaderboard around")
        template = "`{position:>2}` … `{karma:>5}` {username}"

        # get repository parameters
        column = "karma"
        if order == "give":
            column = "positive"
        elif order == "take":
            column = "negative"

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

        if not board or not board.count():
            return None

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

        embed.clear_fields()

        if offset == 0:
            name = self.text.get("board_1", num=limit)
        else:
            name = self.text.get("board_x", num=limit, offset=offset + 1)
        embed.add_field(name=name, value="\n".join(value))

        return embed

    async def checkVoteEmote(self, reaction, user):
        """Check if the emote is vote emote"""
        if not hasattr(reaction, "emoji"):
            return await self._remove_reaction(reaction, user)

        if not reaction.message.content.startswith(self.text.get("vote_info")[:25]):
            return

        if str(reaction.emoji) not in ("☑️", "0⃣", "❎"):
            await self._remove_reaction(reaction, user)

    async def checkBoardEmoji(self, reaction, user):
        """Check if the leaderboard should be scrolled"""
        if user.bot:
            return

        if str(reaction) not in ("⏪", "◀", "▶"):
            return

        # fmt: off
        if len(reaction.message.embeds) != 1 \
        or type(reaction.message.embeds[0].title) != str \
        or not reaction.message.embeds[0].title.startswith(self.text.get("board_title")):
            return
        # fmt: on

        embed = reaction.message.embeds[0]

        # get ordering
        for o in ("desc", "asc", "give", "take"):
            if embed.title.endswith(self.text.get("board_" + o + "_t")):
                order = o
                break

        # get current offset
        if "," in embed.fields[0].name:
            offset = int(embed.fields[0].name.split(" ")[-1]) - 1
        else:
            offset = 0

        # get new offset
        if str(reaction) == "⏪":
            offset = 0
        elif str(reaction) == "◀":
            offset -= self.config.get("leaderboard limit")
        elif str(reaction) == "▶":
            offset += self.config.get("leaderboard limit")

        if offset < 0:
            return await utils.remove_reaction(reaction, user)

        # apply
        embed = self.fillBoard(embed, member=user, order=order, offset=offset)
        if embed:
            await reaction.message.edit(embed=embed)
        await utils.remove_reaction(reaction, user)
