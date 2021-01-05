import discord
from discord.ext import commands


from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from repository.anonpost_repo import AnonPostRepository


class AnonPost(rubbercog.Rubbercog):
    """Send files anonymously"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("anonpost")
        self.config = CogConfig("anonpost")

    @commands.check(acl.check)
    @commands.group()
    async def anonpost(self, ctx):
        """Manage anonymous channels"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @anonpost.command(name="add")
    async def anonpost_add(self, ctx, name: str):
        """Add channel used for anonymous posts"""
        pass

    @commands.check(acl.check)
    @anonpost.command(name="remove")
    async def anonpost_remove(self, ctx):
        """Remove channel used for anonymous posts"""
        pass

    @commands.check(acl.check)
    @anonpost.command(name="rename")
    async def anonpost_rename(self, ctx, name: str):
        """Rename anonymous post channel"""
        pass

    @commands.check(acl.check)
    @commands.command()
    async def anonsend(self, ctx, channel: str):
        """Send image anonymously

        `channel`: Channel code to send the image to.
        """
        pass
        # check channel
        # check image format
        # copy the image
        # clear the exif
        # send it


def setup(bot):
    """Load cog"""
    bot.add_cog(AnonPost(bot))
