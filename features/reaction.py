import datetime
import re

import discord
from discord.ext.commands import Bot

from core.config import config
from core import utils
from config.messages import Messages
from features.base_feature import BaseFeature
from features.review import Review
from repository.karma_repo import KarmaRepository
from repository.review_repo import ReviewRepository

review_r = ReviewRepository()


class Reaction(BaseFeature):
    def __init__(self, bot: Bot, karma_repository: KarmaRepository):
        super().__init__(bot)
        self.karma_repo = karma_repository
        self.review = Review(bot)

    def make_embed(self, page):
        embed = discord.Embed(
            title="Rubbergoddess", description="Rubbergod? Tss.", color=config.color
        )
        prefix = config.prefix
        embed.add_field(name="Autor", value="Cauchy#5244")
        embed.add_field(name="Počet serverů s touto instancí bota", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="\u200b", value="Příkazy:", inline=False)
        info = Messages.info[page - 1]
        for command in info:
            embed.add_field(name=prefix + command[0], value=command[1], inline=False)
        embed.set_footer(
            text=f"Page {page} | Commit {utils.git_hash()}",
            icon_url="https://cdn.discordapp.com/avatars/673134999402184734/d61a5db0c5047080"
            "4b3980567da3a1a0.png?size=32",
        )
        return embed

    async def add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            return
        if channel.type is discord.ChannelType.text:
            guild = channel.guild
        else:
            guild = self.bot.get_guild(config.guild_id)
            if guild is None:
                raise Exception("Nemuzu najit guildu podle config.guild_id")
        member = guild.get_member(payload.user_id)

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.errors.NotFound:
            return

        if member is None or message is None or member.bot:
            return

        if payload.emoji.is_custom_emoji():
            emoji = self.bot.get_emoji(payload.emoji.id)
            if emoji is None:
                emoji = payload.emoji
        else:
            emoji = payload.emoji.name

        if message.content.startswith(Messages.karma_vote_message_hack):
            if emoji not in ["☑️", "0⃣", "❎"]:
                await message.remove_reaction(emoji, member)
            else:
                users = []
                for reaction in message.reactions:
                    users.append(await reaction.users().flatten())
                # Flatten the final list
                users = [x for y in users for x in y]
                if users.count(member) > 1:
                    await message.remove_reaction(emoji, member)
        elif message.embeds and message.embeds[0].title == "Rubbergoddess":
            if emoji in ["◀", "▶"]:
                page = int(message.embeds[0].footer.text[5])
                next_page = self.pagination_next(emoji, page, len(Messages.info))
                if next_page:
                    embed = self.make_embed(next_page)
                    await message.edit(embed=embed)
            try:
                await message.remove_reaction(emoji, member)
            except Exception:
                pass
        elif (
            message.embeds
            and message.embeds[0].title is not discord.Embed.Empty
            and re.match(".* reviews", message.embeds[0].title)
        ):
            subject = message.embeds[0].title.split(" ", 1)[0]
            footer = message.embeds[0].footer.text.split("|")[0]
            pos = footer.find("/")
            try:
                page = int(footer[8:pos])
                max_page = int(footer[(pos + 1) :])
            except ValueError:
                await message.edit(content=Messages.reviews_page_e, embed=None)
                return
            tier_average = message.embeds[0].description[-1]
            if emoji in ["◀", "▶", "⏪"]:
                next_page = self.pagination_next(emoji, page, max_page)
                if next_page:
                    review = review_r.get_subject_reviews(subject)
                    if review.count() >= next_page:
                        review = review.all()[next_page - 1].Review
                        next_page = str(next_page) + "/" + str(max_page)
                        embed = self.review.make_embed(review, subject, tier_average, next_page)
                        if embed.fields[3].name == "Text page":
                            await message.add_reaction("🔼")
                            await message.add_reaction("🔽")
                        else:
                            for emote in message.reactions:
                                if emote.emoji == "🔼":
                                    await message.remove_reaction("🔼", self.bot.user)
                                    await message.remove_reaction("🔽", self.bot.user)
                                    break
                        await message.edit(embed=embed)
            elif emoji in ["👍", "👎", "🛑"]:
                review = review_r.get_subject_reviews(subject)[page - 1].Review
                if str(member.id) != review.discord_id:
                    review_id = review.id
                    if emoji == "👍":
                        self.review.add_vote(review_id, True, str(member.id))
                    elif emoji == "👎":
                        self.review.add_vote(review_id, False, str(member.id))
                    elif emoji == "🛑":
                        review_r.remove_vote(review_id, str(member.id))
                    page = str(page) + "/" + str(max_page)
                    embed = self.review.make_embed(review, subject, tier_average, page)
                    await message.edit(embed=embed)
            elif emoji in ["🔼", "🔽"]:
                if message.embeds[0].fields[3].name == "Text page":
                    review = review_r.get_subject_reviews(subject)
                    if review:
                        review = review[page - 1].Review
                        text_page = message.embeds[0].fields[3].value
                        pos = message.embeds[0].fields[3].value.find("/")
                        max_text_page = int(text_page[(pos + 1) :])
                        text_page = int(text_page[:pos])
                        next_text_page = self.pagination_next(emoji, text_page, max_text_page)
                        if next_text_page:
                            page = str(page) + "/" + str(max_page)
                            embed = self.review.make_embed(review, subject, tier_average, page)
                            embed = self.review.change_text_page(
                                review, embed, next_text_page, max_text_page
                            )
                            await message.edit(embed=embed)
            try:
                await message.remove_reaction(emoji, member)
            except Exception:
                pass  # in DM
        else:
            count = True
            # do not count author's emotes
            if member.id == message.author.id:
                count = False
            # count master and slave guilds
            elif guild.id != config.guild_id and guild.id != config.slave_id:
                count = False
            # do not count banned channels
            elif message.channel.id in config.karma_channels_ban:
                count = False
            # do not count banned roles
            elif config.karma_roles_ban in map(lambda x: x.id, member.roles):
                count = False
            # do not count banned strings
            elif len(config.karma_string_ban) > 0:
                for s in config.karma_string_ban:
                    if s in message.content:
                        count = False
            # optionally, do not count subjects
            elif not config.karma_subjects:
                if (
                    isinstance(message.channel, discord.TextChannel)
                    and message.channel.name in config.subjects
                ):
                    count = False

            if count and isinstance(emoji, str):
                self.karma_repo.karma_emoji(message.author, member, emoji)
            elif count:
                self.karma_repo.karma_emoji(message.author, member, emoji.id)

        # if the message has X or more 'pin' emojis pin the message
        if emoji == "📌":
            for reaction in message.reactions:
                if (
                    reaction.emoji == "📌"
                    and reaction.count >= config.pin_limit
                    and not message.pinned
                ):
                    embed = discord.Embed(title="📌 Auto pin message log", color=config.color)
                    users = await reaction.users().flatten()
                    user_names = ", ".join([user.name for user in users])
                    message_link = (
                        Messages.message_link_prefix
                        + str(message.channel.id)
                        + "/"
                        + str(message.id)
                    )
                    embed.add_field(name="Users", value=user_names)
                    embed.add_field(name="In channel", value=message.channel)
                    embed.add_field(name="Message", value=message_link, inline=False)
                    embed.set_footer(text=datetime.datetime.now().replace(microsecond=0))
                    channel = self.bot.get_channel(config.channel_botlog)
                    await channel.send(embed=embed)
                    try:
                        await message.pin()
                    except discord.HTTPException:
                        break

    async def remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            return
        if channel.type is discord.ChannelType.text:
            guild = channel.guild
        else:
            guild = self.bot.get_guild(config.guild_id)
            if guild is None:
                raise Exception("Nemuzu najit guildu podle config.guild_id")
        member = guild.get_member(payload.user_id)

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.errors.NotFound:
            return

        if member is None or message is None or member.bot:
            return

        if payload.emoji.is_custom_emoji():
            emoji = self.bot.get_emoji(payload.emoji.id)
            if emoji is None:
                emoji = payload.emoji
        else:
            emoji = payload.emoji.name

        count = True
        # do not count author's emotes
        if member.id == message.author.id:
            count = False
        # count master and slave guilds
        elif guild.id != config.guild_id and guild.id != config.slave_id:
            count = False
        # do not count banned channels
        elif message.channel.id in config.karma_channels_ban:
            count = False
        # do not count banned roles
        elif config.karma_roles_ban in map(lambda x: x.id, member.roles):
            count = False
        # do not count banned strings
        elif len(config.karma_string_ban) > 0:
            for s in config.karma_string_ban:
                if s in message.content:
                    count = False
        # optionally, do not count subjects
        elif not config.karma_subjects:
            if (
                isinstance(message.channel, discord.TextChannel)
                and message.channel.name in config.subjects
            ):
                count = False

        if count and isinstance(emoji, str):
            self.karma_repo.karma_emoji_remove(message.author, member, emoji)
        elif count:
            self.karma_repo.karma_emoji_remove(message.author, member, emoji.id)

    def pagination_next(self, emoji, page, max_page):
        if emoji in ["▶", "🔽"]:
            next_page = page + 1
        elif emoji in ["◀", "🔼"]:
            next_page = page - 1
        elif emoji == "⏪":
            next_page = 1
        if 1 <= next_page <= max_page:
            return next_page
        else:
            return 0
