import asyncio
from typing import List, Union

import discord
from discord.ext import commands
from emoji import demojize

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
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
        embed.set_thumbnail(url=member.avatar_url_as(size=256))
        await ctx.send(embed=embed)
        await utils.room_check(ctx)
        await utils.delete(ctx.message)

    @commands.guild_only()
    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @karma.command(name="emoji")
    async def karma_emoji(self, ctx, emoji: Union[discord.Emoji, str]):
        """See emojis's karma"""
        identificator: str = str(getattr(emoji, "id", emoji))
        name: str = str(getattr(emoji, "name", emoji))
        value: int = repo_k.emoji_value_raw(identificator)
        if value is None:
            return await ctx.reply(self.text.get("emoji_not_voted"))

        embed = self.embed(
            ctx=ctx,
            description=self.text.get("emoji_description", name=name),
        )
        embed.add_field(
            name=self.text.get("emoji_value"),
            value=str(value),
        )
        if type(emoji) is discord.Emoji:
            embed.add_field(
                name=self.text.get(
                    "emoji_added",
                    guild=self.sanitise(emoji.guild.name),
                ),
                value=emoji.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                inline=False,
            )
            embed.set_thumbnail(url=emoji.url)

        await ctx.reply(embed=embed)
        await utils.room_check(ctx)

    @commands.guild_only()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.guild)
    @karma.command(name="emojis")
    async def karma_emojis(self, ctx):
        """See karma for all emojis"""
        emojis = ctx.guild.emojis
        content = []

        emojis_positive = self._get_emoji_list(emojis, "1")
        if len(emojis_positive) > 0:
            content.append(self.text.get("emojis_positive"))
            content += self._emojis_to_message(emojis_positive)

        emojis_neutral = self._get_emoji_list(emojis, "0")
        if len(emojis_neutral) > 0:
            content.append(self.text.get("emojis_neutral"))
            content += self._emojis_to_message(emojis_neutral)

        emojis_negative = self._get_emoji_list(emojis, "-1")
        if len(emojis_negative) > 0:
            content.append(self.text.get("emojis_negative"))
            content += self._emojis_to_message(emojis_negative)

        emojis_nonvoted = self.get_nonvoted_emojis(emojis)
        if len(emojis_nonvoted) > 0:
            content.append(self.text.get("emojis_not_voted"))
            content += self._emojis_to_message(emojis_nonvoted)

        if len(content) == 0:
            content.append(self.text.get("no_emojis"))

        line = ""
        for items in [x for x in content]:
            if items[0] != "<":
                # description
                if len(line):
                    await ctx.send(line)
                    line = ""
                await ctx.send(items)
                continue

            if line.count("\n") >= 3:
                await ctx.send(line)
                line = ""

            line += "\n" + items
        await ctx.send(line)

        await utils.room_check(ctx)

    @commands.guild_only()
    @commands.check(acl.check)
    @karma.command(name="vote")
    async def karma_vote(self, ctx, emoji: str = None):
        """Vote for emoji's karma value"""
        await utils.delete(ctx.message)

        if emoji is None:
            nonvoted = self.get_nonvoted_emojis(ctx.guild.emojis)

            if len(nonvoted) == 0:
                return await ctx.author.send(
                    self.text.get("all_emojis_voted", guild=ctx.guild.name)
                )
            emoji = nonvoted[0]

        message = await ctx.send(
            self.text.get(
                "vote_info",
                emoji=emoji,
                time=self.config.get("vote time"),
                limit=self.config.get("vote limit"),
            )
        )
        # set default of zero, so we can run the command multiple times
        repo_k.set_emoji_value(str(self._get_emoji_id(emoji)), 0)

        # add options and vote
        await message.add_reaction("☑️")
        await message.add_reaction("0⃣")
        await message.add_reaction("❎")

        await self.event.sudo(ctx, f"Vote over value of {emoji} started.")
        await asyncio.sleep(self.config.get("vote time") * 60)

        # FIXME Is this neccesary? Can the message be desynchronised?
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
            await self.event.sudo(ctx, f"Vote for {emoji} failed.")
            return await ctx.send(self.text.get("vote_failed", emoji=emoji))

        result = 0
        if positive > negative + neutral:
            result = 1
        elif negative > positive + neutral:
            result = -1

        repo_k.set_emoji_value(str(self._get_emoji_id(emoji)), result)
        await ctx.send(self.text.get("vote_result", emoji=emoji, value=result))
        await self.event.sudo(ctx, f"{emoji} karma value voted as {result}.")

    @commands.check(acl.check)
    @karma.command(name="set")
    async def karma_set(self, ctx, emoji: str, value: int):
        """Set karma value without public vote"""
        repo_k.set_emoji_value(str(self._get_emoji_id(emoji)), value)
        await ctx.send(self.text.get("emoji", emoji=emoji, value=value))
        await self.event.sudo(ctx, f"Karma of {emoji} set to {value}.")

        await utils.delete(ctx)

    # TODO Update embed link: copy style from pin information
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

        count = True
        if message.channel.id in self.config.get("banned channels") or (
            not self.config.get("count subjects") and repo_s.get(message.channel.name) is not None
        ):
            count = False
        for word in self.config.get("banned words"):
            if word in message.content:
                count = False
                break

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
            embed.add_field(
                name=self.text.get("embed_total"),
                value=f"**{karma}**",
                inline=False,
            )
        else:
            embed.add_field(name="\u200b", value=self.text.get("embed_disabled"), inline=False)
        await ctx.reply(embed=embed)

        await utils.room_check(ctx)

    @commands.check(acl.check)
    @karma.command(name="give")
    async def karma_give(self, ctx, member: discord.Member, value: int):
        """Give karma points to someone"""
        repo_k.update_karma(member=member, giver=ctx.author, emoji_value=value)
        await ctx.reply(self.text.get("give", "given" if value > 0 else "taken"))
        await self.event.sudo(ctx, f"{member} got {value} karma points.")

    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @karma.command(aliases=["karmaboard"])
    async def leaderboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.send_leaderboard(ctx, "desc", offset)

    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @karma.command()
    async def loserboard(self, ctx, offset: int = 0):
        """Karma leaderboard, from the worst"""
        await self.send_leaderboard(ctx, "asc", offset)

    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @karma.command()
    async def givingboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.send_leaderboard(ctx, "give", offset)

    @commands.cooldown(rate=3, per=30, type=commands.BucketType.channel)
    @karma.command(aliases=["stealingboard"])
    async def takingboard(self, ctx, offset: int = 0):
        """Karma leaderboard"""
        await self.send_leaderboard(ctx, "take", offset)

    ##
    ## Listeners
    ##
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Karma add"""
        parsed_payload = await self._payload_to_reaction(payload)
        if parsed_payload is None:
            return
        channel, member, message, emote = parsed_payload

        count = self._count_karma(member=member, message=message)
        if not count:
            return

        repo_k.karma_emoji(message.author, member, emote)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Karma remove"""
        parsed_payload = await self._payload_to_reaction(payload)
        if parsed_payload is None:
            return
        channel, member, message, emote = parsed_payload

        count = self._count_karma(member=member, message=message)
        if not count:
            return

        repo_k.karma_emoji_remove(message.author, member, emote)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Scrolling, vote"""
        if user.bot:
            return

        if reaction.message.channel.id == config.get("channels", "vote"):
            await self._check_vote_emoji(reaction, user)

        if str(reaction) in ("⏪", "◀", "▶"):
            await self._check_scroll_emoji(reaction, user)

    ##
    ## Helper functions
    ##
    def _is_unicode_emoji(self, text):
        demojized = demojize(text)
        if demojized.count(":") != 2:
            return False
        if demojized.split(":")[2] != "":
            return False
        return demojized != text

    def _get_emoji_list(self, guild_emojis: list, value: int) -> list:
        db_emojis = repo_k.getEmotesByValue(value)

        result = []
        # Include guild emojis
        for emoji in guild_emojis:
            if str(emoji.id) in db_emojis:
                result.append(emoji)
        # Include unicode emojis
        for emoji in db_emojis:
            if self._is_unicode_emoji(emoji):
                result.append(emoji)

        return result

    def get_nonvoted_emojis(self, guild_emojis: list) -> list:
        db_emojis = [x.emoji_ID for x in repo_k.get_all_emojis()]

        result = []
        for emoji in guild_emojis:
            if str(emoji.id) not in db_emojis:
                result.append(emoji)
        return result

    def _emojis_to_message(self, emotes: list) -> List[str]:
        line = ""
        result = []
        for i, emote in enumerate(emotes):
            if i % 8 == 0:
                result.append(line)
                line = ""
            line += f"{emote} "
        result.append(line)

        return [r for r in result if len(r) > 0]

    def _get_emoji_id(self, emoji: str):
        if ":" in str(emoji):
            return int(str(emoji).split(":")[2][:-1])
        return emoji

    async def _payload_to_reaction(self, payload: discord.RawReactionActionEvent) -> tuple:
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
        except Exception:
            pass

    ##
    ## Logic
    ##
    def _count_karma(self, *, member: discord.Member, message: discord.Message) -> bool:
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

    async def send_leaderboard(self, ctx: commands.Context, parameter: str, offset: int):
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
        embed = self._fill_leaderboard(embed, member=ctx.author, order=parameter, offset=offset)

        message = await ctx.send(embed=embed)
        await message.add_reaction("⏪")
        await message.add_reaction("◀")
        await message.add_reaction("▶")

        await utils.room_check(ctx)
        await utils.delete(ctx.message)

    def _fill_leaderboard(self, embed, *, member, order: str, offset: int) -> discord.Embed:
        limit = self.config.get("leaderboard limit")
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

        user_in_list = False
        for i, db_user in enumerate(board, start=offset):
            # fmt: off
            user = self.getGuild().get_member(int(db_user.discord_id))
            username = (
                self.sanitise(user.display_name)
                if hasattr(user, "display_name")
                else "_unknown_"
            )

            if int(db_user.discord_id) == member.id:
                username = f"**{username}**"
                user_in_list = True

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
        embed.add_field(name=name, value="\n".join(value), inline=False)

        # construct user field, if they are not included in first one
        if not user_in_list:
            k = repo_k.get_karma(member.id)
            # get right values
            if order in ("desc", "asc"):
                value, position = k.karma.value, k.karma.position
            elif order == "give":
                value, position = k.positive.value, k.positive.position
            else:
                value, position = k.negative.value, k.negative.position
            username = "**" + self.sanitise(member.display_name) + "**"

            embed.add_field(
                name=self.text.get("board_user"),
                value=template.format(position=position, karma=value, username=username),
            )

        return embed

    async def _check_vote_emoji(self, reaction, user):
        """Check if the emote is vote emote"""
        if not hasattr(reaction, "emoji"):
            return await self._remove_reaction(reaction, user)

        if not reaction.message.content.startswith(self.text.get("vote_info")[:25]):
            return

        if str(reaction.emoji) not in ("☑️", "0⃣", "❎"):
            await self._remove_reaction(reaction, user)

    async def _check_scroll_emoji(self, reaction, user):
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
            offset = 0

        # apply
        embed = self._fill_leaderboard(embed, member=user, order=order, offset=offset)
        if embed:
            await reaction.message.edit(embed=embed)
        await utils.remove_reaction(reaction, user)
