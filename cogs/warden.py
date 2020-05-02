from io import BytesIO

import discord
from discord.ext import commands
import dhash
from PIL import Image

from core.config import config
from core.emote import emote
from core import check, rubbercog, utils
from repository import image_repo

dhash.force_pil()
repository = image_repo.ImageRepository()

class Warden (rubbercog.Rubbercog):
    """A cog for database lookups"""
    def __init__ (self, bot):
        super().__init__(bot)
        self.visible = False

        self.limit_full = 3
        self.limit_hard = 30
        self.limit_soft = 70

    # apt install libopenjp2-7 libtiff5
    # pip3 install pillow dhash

    @commands.Cog.listener()
    async def on_message (self, message: discord.Message):
        if message.channel.id in config.get('warden cog', 'deduplication channels') \
        and message.attachments is not None:
            await self.checkDuplicate(message)


    async def checkDuplicate(self, message: discord.Message):
        """Check if uploaded files are known"""
        hashes = []
        for f in message.attachments:
            fp = BytesIO()
            await f.save(fp)
            h = dhash.dhash_int(Image.open(fp))
            hashes.append(h)
            h_ = str(hex(h))
            repository.add_image(
                channel_id=message.channel.id,
                message_id=message.id,
                attachment_id=f.id,
                dhash=h_
            )

        duplicate = None
        hamming_min = 128
        for h in hashes:
            limit = None
            posts = repository.getLast(1000)
            for post in posts[:-1]:
                post_hash = int(post.dhash, 16)
                hamming = dhash.get_num_bits_different(h, post_hash)
                if hamming < hamming_min:
                    duplicate = post
                    hamming_min = hamming

        if hamming_min <= self.limit_soft:
            await self._announceDuplicate(message, duplicate, hamming_min)

    async def _announceDuplicate(self, message: discord.Message, duplicate: object, hamming: int):
        """Send message that a post is a duplicate

        limit: Achieved limit. [full|hard|soft]
        duplicate: object
        """
        if hamming <= self.limit_full:
            t = "**:recycle: To je repost!**"
        elif hamming <= self.limit_hard:
            t = "**:recycle: To je asi repost**"
        else:
            t = "To je možná repost"
        prob = "{:.1f} %".format((1 - hamming / 128) * 100)
        timestamp = duplicate.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        link = 'https://discordapp.com/channels/{}/{}/{}'.format(
            self.getGuild().id, duplicate.channel_id, duplicate.message_id)

        embed = discord.Embed(title=t, color=config.color)
        embed.add_field(name=timestamp, value=prob + '\n' + link)
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Warden(bot))
