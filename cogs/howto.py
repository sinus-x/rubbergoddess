import collections
import hjson

import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text


class Howto(rubbercog.Rubbercog):
    """See information about school related topics"""

    def __init__(self, bot):
        super().__init__(bot)

        try:
            self.data = hjson.load(open("data/howto/howto.hjson"))
        except Exception as e:
            print("Could not load HOWTO source")
            self.data = collections.OrderedDict()

    ##
    ## Commands
    ##

    @commands.check(check.is_verified)
    @commands.command()
    async def howto(self, ctx, category: str = None, subcategory: str = None):
        """See information about school related topics"""
        # temp
        content = ""
        embed = self.embed(ctx=ctx)
        for name, value in self._format(content).items():
            embed.add_field(name=name, value=value, inline=False)
        await ctx.send(embed=embed, delete_after=config.get("delay", "help"))

    ##
    ## Helper functions
    ##

    ##
    ## Error catching
    ##

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # try to get original error
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        # non-rubbergoddess exceptions are handled globally
        if not isinstance(error, rubbercog.RubbercogException):
            return

        # fmt: off
        elif isinstance(error, HowtoException):
            await self.output.error(ctx, text.fill(
                "howto",
                "HowtoException",
                mention=ctx.author.mention
            ))
        # fmt: on


def setup(bot):
    bot.add_cog(Howto(bot))


class HowtoException(rubbercog.RubbercogException):
    pass


"""
- eduroam / <class 'collections.OrderedDict'>
  - android / <class 'str'>
  - windows / <class 'str'>
  - linux / <class 'str'>
- horde / <class 'collections.OrderedDict'>
  - login / <class 'str'>
  - přeposílání / <class 'str'>
- koleje / <class 'list'>
- kolejnet / <class 'str'>
- rozvrh / <class 'list'>
- vpn / <class 'collections.OrderedDict'>
  - android / <class 'str'>
  - windows / <class 'str'>
  - macOS   / <class 'str'>
  - linux   / <class 'str'>
"""
