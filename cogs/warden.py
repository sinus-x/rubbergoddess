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

class Warden (rubbercog.Rubbercog):
    """A cog for database lookups"""

    #TODO Implement template matching to prevent false positives
    #TODO Implement ?deepscan to test against all database hashes

    def __init__ (self, bot):
        super().__init__(bot)

        self.limit_full = 3
        self.limit_hard = 7
        self.limit_soft = 14

        self.message_channel = None

    def doCheckRepost(self, message: discord.Message):
        return message.channel.id in config.get('warden cog', 'deduplication channels') \
        and message.attachments is not None and len(message.attachments) > 0 \
        and not message.author.bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # repost check
        if self.doCheckRepost(message):
            await self.checkDuplicate(message)

        # gif check
        if "giphy.com/" in message.content or "tenor.com/" in message.content or "imgur.com/" in message.content:
            await message.channel.send(text.fill('warden', 'gif warning', user=message.author))
            repo_k.update_karma_get(message.author, -5)
            await self.deleteCommand(message)
            self.console.debug("Warden:on_message", "Removed message linking a gif")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if self.doCheckRepost(message):
            i = repo_i.deleteByMessage(message.id)
            self.console.debug("Warden:on_message_delete", f"Removed {i} dhash(es) from database")

            # try to detect repost embed
            messages = await message.channel.history(after=message, limit=10, oldest_first=True).flatten()
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
        """Delete duplicate embed if original is not a duplicate"""
        if payload.channel_id not in config.get('warden cog', 'deduplication channels'):
            return
        if payload.member.bot:
            return
        try:
            message = await self.getGuild().get_channel(payload.channel_id).fetch_message(payload.message_id)
        except Exception as e:
            self.console.debug("Warden:on_raw_reaction_add", "Message not found", e)
            return
        if not message or not message.author.bot:
            return

        for r in message.reactions:
            if r.emoji == '❎' and r.count > config.get('warden cog', 'not duplicate limit'):
                try:
                    orig = message.embeds[0].footer.text
                    orig = await message.channel.fetch_message(int(orig))
                    await orig.remove_reaction('♻️', self.bot.user)
                except Exception as e:
                    self.console.debug("Warden:on_raw_reaction_add", "Could not remove ♻️", e)
                    return
                await message.delete()

    async def checkDuplicate(self, message: discord.Message):
        """Check if uploaded files are known"""
        skipped = False
        hashes = []
        for f in message.attachments:
            fp = BytesIO()
            await f.save(fp)
            try:
                i = Image.open(fp)
            except OSError:
                # not an image
                continue
            h = dhash.dhash_int(i)
            hashes.append(h)
            h_ = str(hex(h))
            repo_i.add_image(
                channel_id=message.channel.id,
                message_id=message.id,
                attachment_id=f.id,
                dhash=h_
            )

        if len(message.attachments) > 0 and len(hashes) == 0:
            await message.add_reaction('▶')
            return

        duplicates = {}
        posts = repo_i.getLast(1000)
        for h in hashes:
            hamming_min = 128
            duplicate = None
            limit = None
            for post in posts:
                # skip current message
                if post.message_id == message.id:
                    continue
                # do the comparison
                post_hash = int(post.dhash, 16)
                hamming = dhash.get_num_bits_different(h, post_hash)
                if hamming < hamming_min:
                    duplicate = post
                    hamming_min = hamming

            duplicates[duplicate] = hamming_min

            await self.output.debug(message.channel, f"Closest Hamming distance: {hamming_min}/128 bits")
            self.console.debug("Warden:checkDuplicate", f"Closest Hamming distance: {hamming_min}/128 bits")

        for d, h in duplicates.items():
            if h <= self.limit_soft:
                await self._announceDuplicate(message, d, h)

    async def _announceDuplicate(self, message: discord.Message, original: object, hamming: int):
        """Send message that a post is a original

        original: object
        hamming: Hamming distance between the image and closest database entry
        """
        if hamming <= self.limit_full:
            t = "**♻️ To je repost!**"
            await message.add_reaction('♻️')
        elif hamming <= self.limit_hard:
            t = "**♻️ To je asi repost**"
            await message.add_reaction('🤔')
        else:
            t = "To je možná repost"
            await message.add_reaction('🤷🏻')
        prob = "{:.1f} %".format((1 - hamming / 128) * 100)
        timestamp = original.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        src_chan = self.getGuild().get_channel(original.channel_id)
        try:
            src_post = await src_chan.fetch_message(original.message_id)
            link = src_post.jump_url
            author = discord.utils.escape_markdown(src_post.author.display_name)
        except:
            link = "404 " + emote.sad
            author = "_??? (404)_"

        d = text.fill('warden', 'repost description', name=discord.utils.escape_markdown(message.author.display_name), value=prob)
        embed = discord.Embed(title=t, color=config.color, description=d, url=message.jump_url)
        embed.add_field(name=f"**{author}**, {timestamp}", value=link, inline=False)

        embed.add_field(name=text.get('warden', 'repost title'),
            value='_'+text.fill('warden', 'repost content',
                limit=config.get('warden cog', 'not duplicate limit'))+'_')
        embed.set_footer(text=message.id)
        m = await message.channel.send(embed=embed)
        await m.add_reaction('❎')

def setup(bot):
    bot.add_cog(Warden(bot))
