import datetime

from discord.ext import commands

from core import rubbercog, utils
from core.config import config

boottime = datetime.datetime.now().replace(microsecond=0)


class Base(rubbercog.Rubbercog):
    """About"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def uptime(self, ctx):
        """Bot uptime"""
        now = datetime.datetime.now().replace(microsecond=0)
        delta = now - boottime

        embed = self.embed(ctx)
        embed.add_field(name="Boot", value=str(boottime), inline=False)
        embed.add_field(name="Uptime", value=str(delta), inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)

    @commands.command()
    async def ping(self, ctx):
        """Bot latency"""
        await ctx.send("pong: **{:.2f} s**".format(self.bot.latency))


def setup(bot):
    bot.add_cog(Base(bot))
