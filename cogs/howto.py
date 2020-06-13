import hjson

import discord
from discord.ext import commands

from core import check, exceptions, rubbercog, utils
from core.config import config
from core.text import text


class Howto(rubbercog.Rubbercog):
    """Verify your account"""

    def __init__(self, bot):
        super().__init__(bot)

        try:
            self.data = hjson.load(open("data/howto/howto.hjson"))
        except Exception as e:
            print(e)
            self.data = {}

    ##
    ## Commands
    ##

    @commands.check(check.is_verified)
    @commands.command()
    async def howto(self, ctx, category: str = None, subcategory: str = None):
        if category is None:
            # TODO Display known categories instead
            return await utils.send_help(ctx)

        if category in self.data and not subcategory:
            data = self.data[category]
        elif subcategory is not None and subcategory in data:
            data = self.data[category][subcategory]
        else:
            raise HowtoException()

        embed = discord.Embed(title="How to... " + category, color=config.color)
        for key, value in data.items():
            embed.add_field(name=key.upper(), value=value, inline=False)
        await ctx.send(embed=embed)

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
        if not isinstance(error, exceptions.RubbergoddessException):
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


class HowtoException(exceptions.RubbergoddessException):
    pass
