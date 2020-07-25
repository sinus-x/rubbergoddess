import hjson
from collections import OrderedDict

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
        except:
            print("Howto init(): Could not load HOWTO source file.")  # noqa: T001
            self.data = OrderedDict()

    ##
    ## Commands
    ##

    @commands.check(check.is_verified)
    @commands.command()
    async def howto(self, ctx, *args):
        """See information about school related topics"""
        args = [x for x in args if len(x) > 0]

        name = "\u200b"
        content = self.data

        # get the requested item
        for directory in args:
            if directory not in content.keys():
                await utils.delete(ctx)
                raise HowtoException()
            name = directory
            content = content.get(name)

        title = "{prefix}{command} {args}".format(
            prefix=config.prefix,
            command=ctx.command.qualified_name,
            args=self.sanitise(" ".join(args), limit=30),
        )
        embed = self.embed(ctx=ctx, title=title)

        # fill the embed
        if isinstance(content, OrderedDict):
            embed = self._add_listing(embed, name, content)
        elif isinstance(content, list):
            embed = self._add_list_content(embed, name, content)
        else:
            embed = self._add_str_content(embed, name, str(content))

        # done
        await ctx.send(embed=embed, delete_after=config.get("delay", "help"))
        await utils.delete(ctx)

    ##
    ## Helper functions
    ##

    def _add_listing(self, embed: discord.Embed, name: str, directory: OrderedDict):
        """List items in howto directory

        name: directory name
        directory: howto category (HJSON {})
        """
        value = "\n".join(["→ " + x for x in directory.keys()])
        embed.add_field(name=name, value=value)
        return embed

    def _add_list_content(self, embed: discord.Embed, name: str, item: list):
        """Add item content to embed

        name: item name
        item: list
        """
        for i, step in enumerate(item):
            embed.add_field(name=f"#{i+1}", value=step, inline=False)
        return embed

    def _add_str_content(self, embed: discord.Embed, name: str, item: str):
        """Add item content to embed

        name: item name
        item: string
        """
        embed.add_field(name="\u200b", value=item)
        return embed

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
            await self.output.warning(ctx, text.fill(
                "howto",
                "HowtoException",
                mention=ctx.author.mention
            ))
        # fmt: on


def setup(bot):
    bot.add_cog(Howto(bot))


class HowtoException(rubbercog.RubbercogException):
    pass
