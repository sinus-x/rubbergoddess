import asyncio
import dhash
import time
from io import BytesIO
from PIL import Image

import discord
from discord.ext import commands

from core import acl, rubbercog, utils
from cogs.resource import CogConfig, CogText
from core.config import config
from core.emote import emote
from repository import image_repo

dhash.force_pil()
repo_i = image_repo.ImageRepository()


class Warden(rubbercog.Rubbercog):
    """Repost detector"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("warden")
        self.text = CogText("warden")

        self.limit_full = 3
        self.limit_hard = 7
        self.limit_soft = 14

    @commands.check(acl.check)
    @commands.group()
    async def scan(self, ctx):
        """Scan for reposts"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.bot_has_permissions(read_message_history=True)
    @scan.command(name="history")
    async def scan_history(self, ctx, limit: int):
        """Scan current channel for images and save them as hashes.

        limit: How many messages should be scanned. Negative to scan all.
        """
        if limit < 0:
            limit = None

        async with ctx.typing():
            messages = await ctx.channel.history(limit=limit).flatten()

        status = await ctx.send(self.text.get("scan_history", "title", count=len(messages)))

        await asyncio.sleep(1)

        ctr_nofile: int = 0
        ctr_hashes: int = 0
        now = time.time()
        for i, message in enumerate(messages, 1):
            if i % 20 == 0:
                await status.edit(
                    content=self.text.get(
                        "scan_history",
                        "scanning",
                        count=i,
                        total=len(messages),
                        percent="{:.1f}".format(i / len(messages) * 100),
                        hashes=ctr_hashes,
                    )
                )

            if not len(message.attachments):
                ctr_nofile += 1
                continue

            hashes = [x async for x in self.save_hashes(message)]
            ctr_hashes += len(hashes)

        await status.edit(
            content=self.text.get(
                "scan_history",
                "complete",
                messages=len(messages),
                hashes=ctr_hashes,
                seconds="{:.1f}".format(time.time() - now),
            )
        )

    @commands.check(acl.check)
    @scan.command(name="compare", aliases=["messages"])
    async def scan_compare(self, ctx, messages: commands.Greedy[discord.Message]):
        """Display hashes of given messages.

        messages: Space separated list of messages.
        """
        text = []

        for message in messages:
            db_images = repo_i.get_by_message(message.id)
            if not len(db_images):
                continue

            text.append(self.text.get("compare", "header", message_id=message.id))
            for db_image in db_images:
                text.append(self.text.get("compare", "line", hash=db_image.dhash[2:]))
            text.append("")

        if not len(text):
            return await ctx.send("compare", "not_found")

        await ctx.send("\n".join(text))

    #

    def _in_repost_channel(self, message: discord.Message) -> bool:
        if message.channel.id not in self.config.get("deduplication channels"):
            return False
        if message.attachments is None or not len(message.attachments):
            return False
        if message.author.bot:
            return False
        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self._in_repost_channel(message):
            await self.check_message(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        repo_i.delete_by_message(payload.message_id)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not self._in_repost_channel(message):
            return

        # try to detect and delete repost embed
        messages = await message.channel.history(
            after=message, limit=3, oldest_first=True
        ).flatten()
        for report in messages:
            if not report.author.bot:
                continue
            if len(report.embeds) != 1 or type(report.embeds[0].footer.text) != str:
                continue
            if str(message.id) != report.embeds[0].footer.text.split(" | ")[1]:
                continue

            try:
                await report.delete()
            except discord.HTTPException as e:
                await self.console.error(message, "Could not delete repost report.", e)
            break

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle 'This is a repost' report.

        The footer contains reposter's user ID and repost message id.
        """
        if reaction.message.channel.id not in self.config.get("deduplication channels"):
            return
        if user.bot:
            return
        if not reaction.message.author.bot:
            return
        emoji = str(reaction.emoji)
        if emoji != "❎":
            return

        try:
            repost_message_id = int(reaction.message.embeds[0].footer.text.split(" | ")[1])
            repost_message = await reaction.message.channel.fetch_message(repost_message_id)
        except discord.errors.HTTPException:
            return await self.console.error(reaction.message, "Could not find the repost message.")

        for report_reaction in reaction.message.reactions:
            if str(report_reaction) != "❎":
                continue

            if (
                emoji == "❎"
                and str(report_reaction) == "❎"
                and report_reaction.count > self.config.get("not duplicate limit")
            ):
                # remove bot's reaction, it is not a repost
                try:
                    await repost_message.remove_reaction("♻️", self.bot.user)
                    await repost_message.remove_reaction("🤷🏻", self.bot.user)
                    await repost_message.remove_reaction("🤔", self.bot.user)
                except discord.errors.HTTPException as exc:
                    return await self.console.error(
                        reaction.message, "Could not remove bot's reaction.", exc
                    )
                return await utils.delete(reaction.message)

    #

    async def save_hashes(self, message: discord.Message):
        for attachment in message.attachments:
            if attachment.size > self.config.get("max_size") * 1024:
                continue

            extension = attachment.filename.split(".")[-1].lower()
            if extension not in ("jpg", "jpeg", "png", "webp", "gif"):
                continue

            fp = BytesIO()

            await attachment.save(fp)
            try:
                image = Image.open(fp)
            except OSError:
                continue

            h = dhash.dhash_int(image)
            repo_i.add_image(
                channel_id=message.channel.id,
                message_id=message.id,
                attachment_id=attachment.id,
                dhash=str(hex(h)),
            )
            yield h

    async def check_message(self, message: discord.Message):
        """Check if message contains duplicate image."""
        image_hashes = [x async for x in self.save_hashes(message)]

        if len(message.attachments) > len(image_hashes):
            await message.add_reaction("▶")
            await asyncio.sleep(2)
            await message.remove_reaction("▶", self.bot.user)

        duplicates = {}
        all_images = None

        for image_hash in image_hashes:
            # try to look up hash directly
            images = repo_i.get_hash(str(hex(image_hash)))
            for image in images:
                # skip current message
                if image.message_id == message.id:
                    continue
                # add to duplicates
                duplicates[image] = 0
                await self.console.debug(message, "Full dhash match found.")
                break

            # move on to the next hash
            continue

            # full match not found, iterate over whole database
            if all_images is None:
                all_images = repo_i.get_all()

            minimal_distance = 128
            duplicate = None
            for image in all_images:
                # skip current image
                if image.message_id == message.id:
                    continue

                # do the comparison
                db_image_hash = int(image.dhash, 16)
                distance = dhash.get_num_bits_different(db_image_hash, image_hash)
                if distance < minimal_distance:
                    duplicate = image
                    minimal_distance = distance

            if minimal_distance < self.limit_soft:
                duplicates[duplicate] = minimal_distance

        for image_hash, distance in duplicates.items():
            await self.report_duplicate(message, image_hash, distance)

    async def report_duplicate(self, message: discord.Message, original: object, distance: int):
        """Send report.

        message: The new message containing attachment repost.
        original: The original attachment.
        distance: Hamming distance between the original and repost.
        """
        if distance <= self.limit_full:
            level = "title_full"
            await message.add_reaction("♻️")
        elif distance <= self.limit_hard:
            level = "title_hard"
            await message.add_reaction("🤔")
        else:
            level = "title_soft"
            await message.add_reaction("🤷🏻")

        similarity = "{:.1f} %".format((1 - distance / 128) * 100)
        timestamp = utils.id_to_datetime(original.attachment_id).strftime("%Y-%m-%d %H:%M:%S")

        try:
            original_channel = message.guild.get_channel(original.channel_id)
            original_message = await original_channel.fetch_message(original.message_id)
            author = discord.utils.escape_markdown(original_message.author.display_name)
            link = (f"[**{author}**, {timestamp}]({original_message.jump_url})",)
        except discord.errors.NotFound:
            link = "404 " + emote.sad

        description = self.text.get(
            "report",
            "description",
            name=discord.utils.escape_markdown(message.author.display_name),
            similarity=similarity,
        )
        embed = discord.Embed(
            title=self.text.get("report", level),
            color=config.color,
            description=description,
        )
        embed.add_field(
            name=self.text.get("report", "original"),
            value=link,
            inline=False,
        )
        embed.add_field(
            name=self.text.get("report", "help"),
            value=self.text.get(
                "report",
                "help_content",
                limit=self.config.get("not duplicate limit"),
            ),
            inline=False,
        )
        embed.set_footer(text=f"{message.author.id} | {message.id}")
        report = await message.reply(embed=embed)
        await report.add_reaction("❎")


def setup(bot):
    """Load cog"""
    bot.add_cog(Warden(bot))
