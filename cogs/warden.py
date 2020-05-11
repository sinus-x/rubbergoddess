from io import BytesIO

import discord
from discord.ext import commands
import dhash
from PIL import Image

from core.config import config
from core.emote import emote
from core import check, rubbercog, utils
from repository import image_repo, karma_repo

dhash.force_pil()
repository = image_repo.ImageRepository()
repo_k = karma_repo.KarmaRepository()

class Warden (rubbercog.Rubbercog):
    """A cog for database lookups"""

    #TODO Implement template matching to prevent false positives
    #TODO Implement ?deepscan to test against all database hashes
    #TODO Switch generic check boxes for custom guild emotes
    #TODO Remove reactions from trigger image on embed deletion
    #TODO If the check is clicked by author, remove trigger message, too
    #TODO Move fetch_message to checkDuplicate()
    #TODO  Remove deleted messages (404s) from database
    #TODO Send full list of matches to _announceDuplicate()

    #TODO Use strings from text.json

    def __init__ (self, bot):
        super().__init__(bot)
        self.visible = False

        self.limit_full = 3
        self.limit_hard = 7
        self.limit_soft = 14

    # apt install libopenjp2-7 libtiff5
    # pip3 install pillow dhash

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # repost check
        if message.channel.id in config.get('warden cog', 'deduplication channels') \
        and message.attachments is not None and len(message.attachments) > 0 \
        and not message.author.bot:
            return await self.checkDuplicate(message)

        # gif check
        if "https://giphy.com/" in message.content or "https://tenor.com/" in message.content:
            await message.channel.send(
                f"{message.author.mention}, Giphy ani Tenor tu nemáme rádi. Odebrala jsem ti pět karma bodů.")
            repo_k.update_karma_get(message.author, -5)
            await self.deleteCommand(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id not in config.get('warden cog', 'deduplication channels'):
            return
        if payload.member.bot:
            return
        message = await self.getGuild().get_channel(payload.channel_id).fetch_message(payload.message_id)
        if not message or not message.author.bot:
            return

        ctr_crss = 0
        ctr_tick  = 0
        for r in message.reactions:
            if r.emoji == '❎':
                ctr_crss = r.count-1
            elif r.emoji == '☑️':
                ctr_tick = r.count-1

        if ctr_crss > ctr_tick and ctr_crss > config.get('warden cog', 'not duplicate limit'):
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
            repository.add_image(
                channel_id=message.channel.id,
                message_id=message.id,
                attachment_id=f.id,
                dhash=h_
            )

        if len(message.attachments) > 0 and len(hashes) == 0:
            await message.add_reaction('▶')
            return

        duplicates = {}
        posts = repository.getLast(1000)
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

    async def _announceDuplicate(self, message: discord.Message, duplicate: object, hamming: int):
        """Send message that a post is a duplicate

        limit: Achieved limit. [full|hard|soft]
        duplicate: object
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
        timestamp = duplicate.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        src_chan = self.getGuild().get_channel(duplicate.channel_id)
        src_post = await src_chan.fetch_message(duplicate.message_id)

        embed = discord.Embed(title=t, color=config.color, description='Shoda **{}**'.format(prob))
        embed.add_field(name='Timestamp', value=timestamp)
        embed.add_field(name='Autor', value=src_post.author.mention)
        embed.add_field(name='Link', value=src_post.jump_url, inline=False)
        embed.add_field(name="Co mám dělat?",
            value="_Pokud jde o repost, klikněte na ☑️ a autorovi dejte ♻️.\n" + \
                "Jestli to repost není, klikněte na ❎. Při {} křížkách se toto upozornění smaže._".format(
                    config.get('warden cog', 'not duplicate limit')))
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        m = await message.channel.send(embed=embed)
        await m.add_reaction('☑️')
        await m.add_reaction('❎')

def setup(bot):
    bot.add_cog(Warden(bot))
