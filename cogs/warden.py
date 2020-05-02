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

    # apt install libopenjp2-7 libtiff5
    # pip3 install pillow dhash

    @commands.Cog.listener()
    async def on_message (self, message: discord.Message):
        if message.channel.id in config.get('warden cog', 'deduplication channels') \
        and message.attachments is not None:
            await self.checkDuplicate(message)


    async def checkDuplicate(self, message: discord.Message):
        """Check if uploaded files are known"""
        
        # get file hash and save it
        hashes = []
        for f in message.attachments:
            fp = BytesIO()
            await f.save(fp)
            h = dhash.dhash_int(Image.open(fp))
            h = str(hex(h))
            hashes.append(h)
            repository.add_image(
                channel_id=message.channel.id,
                message_id=message.id,
                attachment_id=f.id,
                dhash=h
            )


        duplicates = {}
        
        # try to search duplicates directly
        for h in hashes:
            match = repository.getHash(h)
            if match:
                if not isinstance(match, list) or len(match) == 1:
                    # this means that single object was returned:
                    # the currently checked post
                    return
                for m in match[:-1]:
                    # 100 %, as they match fully
                    duplicates[m] = 1

            if len(duplicates) > 0:
                await self._announceDuplicate(message, duplicates)
                return

        # extract last X items and iterate
        


    async def _announceDuplicate(self, message: discord.Message, duplicates: dict):
        """Send message that a post is a duplicate

        url: link to duplicate image
        duplicate: dictionary {object: probability}
        """
        embed = discord.Embed(title="**:recycle: To je repost!**", color=config.color)
        guild_id = self.getGuild().id
        for d in duplicates:
            timestamp = d.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            link = 'https://discordapp.com/channels/{}/{}/{}'.format(
                guild_id, d.channel_id, d.message_id)
            embed.add_field(name=timestamp, value=link)

        await message.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Warden(bot))
