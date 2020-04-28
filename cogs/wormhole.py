from io import BytesIO

import discord
from discord.ext import commands

from core import config, rubbercog, text

class Wormhole(rubbercog.Rubbercog):
    """Allow sending messages between servers"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False
        self.wormhole = None

        self.received = 0
        self.sent = 0

    @commands.Cog.listener()
    async def on_message (self, message):
        # do not act if not in wormhole
        if message.channel.id not in config.wormhole_distant:
            return
        # do not act if author is bot
        if message.author.bot:
            self.sent += 1
            return

        # check availability of local wormhole channel
        if self.wormhole is None:
            self.wormhole = self.getGuild().get_channel(config.wormhole_local)

        content = None
        files = []
        # copy remote message
        if message.content:
            if config.wormhole_anonymise:
                content = "> " + message.content
            else:
                content = f"**{discord.utils.escape_mentions(message.author.name)}**: {message.content}"
        if message.attachments:
            for f in message.attachments:
                fp = BytesIO()
                await f.save(fp)
                files.append(discord.File(fp, filename=f.filename, spoiler=f.is_spoiler()))
        # send the message
        self.received += 1
        await self.wormhole.send(content=content, files=files)

    @commands.command()
    async def wormhole(self, ctx: commands.Context):
        """Wormhole statistics"""
        await ctx.send(text.fill("wormhole", "statistics", sent=self.sent, received=self.received))

def setup(bot):
    bot.add_cog(Wormhole(bot))
