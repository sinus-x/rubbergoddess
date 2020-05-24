from random import choice

import discord
from discord.ext import commands

from core.config import config
from core.text import text
from core.emote import emote
from core import rubbercog, utils
from config.messages import Messages as messages


class Meme(rubbercog.Rubbercog):
    """Interact with users"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command(name="???", aliases=["??"])
    async def question(self, ctx):
        """What?"""
        await ctx.send(choice(messages.question))

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """Hug someone!

        user: Discord user. If none, the bot will hug yourself."""
        if user is None:
            user = ctx.author
        elif user == self.bot.user:
            await ctx.send(emote.hug_left)
            return

        await ctx.send(emote.hug_right + f" **{discord.utils.escape_markdown(user.display_name)}**")

    @hug.error
    async def hugError(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(text.get("error", "no user"))


def setup(bot):
    bot.add_cog(Meme(bot))
