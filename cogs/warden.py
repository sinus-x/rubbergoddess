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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # repost check
        if message.channel.id in config.get('warden cog', 'deduplication channels') \
        and message.attachments is not None and len(message.attachments) > 0 \
        and not message.author.bot:
            return await self.checkDuplicate(message)

        # gif check
        if "giphy.com/" in message.content or "tenor.com/" in message.content or "imgur.com/" in message.content:
            await message.channel.send(text.fill('warden', 'gif warning', user=message.author))
            repo_k.update_karma_get(message.author, -5)
            await self.deleteCommand(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.attachments is not None:
            repo_i.deleteByMessage(message.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Delete duplicate embed if original is not a duplicate"""
        if payload.channel_id not in config.get('warden cog', 'deduplication channels'):
            return
        if payload.member.bot:
            return
        message = await self.getGuild().get_channel(payload.channel_id).fetch_message(payload.message_id)
        if not message or not message.author.bot:
            return

        for r in message.reactions:
            if r.emoji == '❎' and r.count > config.get('warden cog', 'not duplicate limit'):
                try:
                    orig = message.embeds[0].footer.text
                    orig = await message.channel.fetch_message(int(orig))
                    await orig.remove_reaction('♻️', self.bot.user)
                except Exception as e:
                    #TODO Log unaccesable message
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
            for post in posts[:-1]:
                post_hash = int(post.dhash, 16)
                hamming = dhash.get_num_bits_different(h, post_hash)
                if hamming < hamming_min:
                    duplicate = post
                    hamming_min = hamming

            duplicates[duplicate] = hamming_min

            if config.debug >= 2:
                await message.channel.send(
                    "```DEBUG 2:\nClosest hamming distance: {} (out of 128 bits)```".format(hamming_min))

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
        src_post = await src_chan.fetch_message(original.message_id)
        if src_post is not None:
            link = src_post.jump_url
            author = discord.utils.escape_markdown(src_post.author.display_name)
        else:
            link = "404 " + emote.sad
            author = "_??? (404)_"

        d = "{}, shoda **{}**!".format(discord.utils.escape_markdown(message.author.display_name), prob)

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
