import asyncio
import time
from io import BytesIO

import discord
from discord.ext import commands
import dhash
from PIL import Image

from core import check, rubbercog, utils
from core.config import config
from core.emote import emote
from core.text import text
from repository import image_repo, karma_repo

dhash.force_pil()
repo_i = image_repo.ImageRepository()
repo_k = karma_repo.KarmaRepository()


class Warden(rubbercog.Rubbercog):
    """A cog for database lookups"""

    # TODO Implement template matching to prevent false positives

    def __init__(self, bot):
        super().__init__(bot)

        self.limit_full = 3
        self.limit_hard = 7
        self.limit_soft = 14

    def doCheckRepost(self, message: discord.Message):
        return (
            message.channel.id in config.get("warden", "deduplication channels")
            and message.attachments is not None
            and len(message.attachments) > 0
            and not message.author.bot
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # repost check - test for duplicates
        if self.doCheckRepost(message):
            if len(message.attachments) > 0:
                await self.checkDuplicate(message)

        # gif check
        for link in config.get("warden", "penalty strings"):
            if link in message.content:
                penalty = config.get("warden", "penalty value")
                await message.channel.send(
                    text.fill("warden", "gif warning", user=message.author, value=penalty)
                )
                repo_k.update_karma_get(message.author, -1 * penalty)
                await utils.delete(message)
                await self.console.debug(message, f"Removed message linking to {link}")
                break

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if self.doCheckRepost(message):
            i = repo_i.deleteByMessage(message.id)
            await self.console.debug(self, f"Removed {i} dhash(es) from database")

            # try to detect repost embed
            messages = await message.channel.history(
                after=message, limit=10, oldest_first=True
            ).flatten()
            for m in messages:
                if not m.author.bot:
                    continue
                try:
                    if str(message.id) == m.embeds[0].footer.text:
                        await m.delete()
                except:
                    continue

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle 'This is a repost' embed"""
        if payload.channel_id not in config.get("warden", "deduplication channels"):
            return
        if payload.member.bot:
            return
        if not hasattr(payload.emoji, "name") or payload.emoji.name not in ("🆗", "❎"):
            return

        try:
            embed_message = (
                await self.getGuild()
                .get_channel(payload.channel_id)
                .fetch_message(payload.message_id)
            )
        except Exception as e:
            return await self.console.debug(self, "Reaction's message not found", e)
        if not embed_message or not embed_message.author.bot:
            return

        try:
            repost_message = embed_message.embeds[0].footer.text.split(" | ")[1]
            repost_message = await embed_message.channel.fetch_message(int(repost_message))
        except Exception as e:
            return await self.console.debug(embed_message, "Could not find repost's original.")

        for r in embed_message.reactions:
            if r.emoji not in ("🆗", "❎"):
                continue

            if (
                payload.emoji.name == "❎"
                and r.emoji == "❎"
                and r.count > config.get("warden", "not duplicate limit")
            ):
                # remove bot's reactions, it is not a repost
                try:
                    await repost_message.remove_reaction("♻️", self.bot.user)
                    await repost_message.remove_reaction("🤷🏻", self.bot.user)
                    await repost_message.remove_reaction("🤔", self.bot.user)
                except Exception as e:
                    await self.console.debug(embed_message, "Could not remove bot's reaction", e)
                    return
                await embed_message.delete()

            elif payload.emoji.name == "🆗" and r.emoji == "🆗":
                # get original author's ID
                repost_author_id = embed_message.embeds[0].footer.text.split(" | ")[0]
                if str(repost_message.author.id) != repost_author_id:
                    return await embed_message.remove_reaction("🆗", embed_message.author)
                # contract the embed
                info_field = embed_message.embeds[0].fields[0]
                embed = discord.Embed()
                embed.add_field(name=info_field.name, value=info_field.value)
                embed.set_footer(text=embed_message.embeds[0].footer.text)
                try:
                    await embed_message.edit(embed=embed)
                    await r.clear()
                except discord.NotFound:
                    pass

    async def saveMessageHashes(self, message: discord.Message):
        for f in message.attachments:
            # FIXME Can we check that the file is image before downloading it?
            fp = BytesIO()
            await f.save(fp)
            try:
                i = Image.open(fp)
            except OSError:
                # not an image
                continue
            h = dhash.dhash_int(i)

            # fmt: off
            repo_i.add_image(
                channel_id=message.channel.id,
                message_id=message.id,
                attachment_id=f.id,
                dhash=str(hex(h)),
            )
            # fmt: on
            yield h

    @commands.group()
    @commands.check(check.is_mod)
    async def scan(self, ctx):
        """Scan for reposts"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.bot_has_permissions(read_message_history=True)
    @scan.command(name="history")
    async def scan_history(self, ctx, limit):
        """Scan current channel for images and save them as hashes

        limit: [all | <int>]
        """
        # parse parameter
        if limit == "all":
            limit = None
        else:
            try:
                limit = int(limit)
                if limit < 1:
                    raise ValueError
            except ValueError:
                raise commands.BadArgument("Expected 'all' or positive integer")

        messages = await ctx.channel.history(limit=limit).flatten()

        # fmt: off
        title = "**INITIATING...**\n\nLoaded {} messages"
        await asyncio.sleep(0.5)
        template = (
            "**SCANNING IN PROGRESS**\n\n"
            "Processed **{}** of **{}** messages ({:.1f} %)\n"
            "Computed **{}** hashes"
        )
        # fmt: on
        msg = await ctx.send(title.format(len(messages)))

        ctr_nofile = 0
        ctr_hashes = 0
        i = 0
        now = time.time()
        for i, message in enumerate(messages):
            # update info on every 10th message
            if i % 20 == 0:
                # fmt: off
                await msg.edit(content=template.format(
                    i, len(messages), (i / len(messages) * 100),
                    ctr_hashes
                ))
                # fmt: on

            if len(message.attachments) == 0:
                ctr_nofile += 1
                continue

            hashes = [x async for x in self.saveMessageHashes(message)]
            ctr_hashes += len(hashes)

        # fmt: off
        await msg.edit(content=
            "**SCAN COMPLETE**\n\n"
            f"Processed **{len(messages)}** messages.\n"
            f"Computed **{ctr_hashes}** hashes in {(time.time() - now):.1f} seconds."
        )
        # fmt: on

    @scan.command(name="message", hidden=True)
    async def scan_message(self, ctx, link):
        """Scan message attachments in whole database"""
        pass

    async def checkDuplicate(self, message: discord.Message):
        """Check if uploaded files are known"""
        hashes = [x async for x in self.saveMessageHashes(message)]

        if len(message.attachments) > 0 and len(hashes) == 0:
            await message.add_reaction("▶")
            await asyncio.sleep(2)
            await message.remove_reaction("▶", self.bot.user)
            return

        duplicates = {}
        posts_all = None
        for image_hash in hashes:
            # try to look up hash directly
            posts_full = repo_i.getHash(str(hex(image_hash)))

            if len(posts_full) > 0:
                # full match found
                for post in posts_full:
                    # skip current message
                    if post.message_id == message.id:
                        continue
                    # add to duplicates
                    duplicates[post] = 0
                    await self.console.debug(message, "Full dhash match")
                    break

                # move on to the next hash
                continue

            # full match not found, iterate over whole database
            if posts_all is None:
                posts_all = repo_i.getAll()

            hamming_min = 128
            duplicate = None
            for post in posts_all:
                # skip current message
                if post.message_id == message.id:
                    continue
                # do the comparison
                post_hash = int(post.dhash, 16)
                hamming = dhash.get_num_bits_different(image_hash, post_hash)
                if hamming < hamming_min:
                    duplicate = post
                    hamming_min = hamming

            duplicates[duplicate] = hamming_min

            await self.console.debug(message, f"Closest Hamming distance: {hamming_min}/128 bits")

        for image_hash, hamming_distance in duplicates.items():
            if hamming_distance <= self.limit_soft:
                await self._announceDuplicate(message, image_hash, hamming_distance)

    async def _announceDuplicate(self, message: discord.Message, original: object, hamming: int):
        """Send message that a post is a original

        original: object
        hamming: Hamming distance between the image and closest database entry
        """
        if hamming <= self.limit_full:
            t = "**♻️ To je repost!**"
            await message.add_reaction("♻️")
        elif hamming <= self.limit_hard:
            t = "**♻️ To je asi repost**"
            await message.add_reaction("🤔")
        else:
            t = "To je možná repost"
            await message.add_reaction("🤷🏻")

        prob = "{:.1f} %".format((1 - hamming / 128) * 100)
        timestamp = utils.id_to_datetime(original.attachment_id).strftime("%Y-%m-%d %H:%M:%S")

        src_chan = self.getGuild().get_channel(original.channel_id)
        try:
            src_post = await src_chan.fetch_message(original.message_id)
            link = src_post.jump_url
            author = discord.utils.escape_markdown(src_post.author.display_name)
        except:
            link = "404 " + emote.sad
            author = "_??? (404)_"

        d = text.fill(
            "warden",
            "repost description",
            name=discord.utils.escape_markdown(message.author.display_name),
            value=prob,
        )
        embed = discord.Embed(title=t, color=config.color, description=d, url=message.jump_url)
        embed.add_field(name=f"**{author}**, {timestamp}", value=link, inline=False)

        embed.add_field(
            name=text.get("warden", "repost title"),
            value="_"
            + text.fill(
                "warden", "repost content", limit=config.get("warden", "not duplicate limit")
            )
            + "_",
        )
        embed.set_footer(text=f"{message.author.id} | {message.id}")
        m = await message.channel.send(embed=embed)
        await m.add_reaction("❎")
        await m.add_reaction("🆗")


def setup(bot):
    bot.add_cog(Warden(bot))
