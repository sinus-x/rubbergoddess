from discord.ext import commands

from cogs.resource import CogText
from core import rubbercog, utils


class Account(rubbercog.Rubbercog):
    """Manage the bot account"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("account")

    @commands.is_owner()
    @commands.group(name="set")
    async def set(self, ctx):
        """Set attributes"""
        await utils.send_help(ctx)

    @set.command(name="name", aliases=["username"])
    async def set_name(self, ctx, *, name: str):
        """Set bot name"""
        await self.bot.user.edit(username=name)
        await ctx.send(self.text.get("name", "ok", name=name))

    @set.command(name="avatar", aliases=["image"])
    async def set_avatar(self, ctx, *, path: str):
        """Set bot avatar

        path: path to image file, starting in `data/` directory
        """
        if ".." in path:
            return await self.output.error(ctx, self.text.get("avatar", "invalid"))

        try:
            with open("data/" + path, "rb") as image:
                with ctx.typing():
                    await self.bot.user.edit(avatar=image.read())
        except FileNotFoundError:
            return await self.output.error(ctx, self.text.get("avatar", "not_found"))
        await ctx.send(self.text.get("avatar", "ok"))
