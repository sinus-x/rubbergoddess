import datetime

import discord
from discord.ext import commands

from core import config, rubbercog
from features import reaction
from repository import karma_repo

karma_r = karma_repo.KarmaRepository()
boottime = datetime.datetime.now().replace(microsecond=0)

class Base (rubbercog.Rubbercog):
    """About"""
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.reaction = reaction.Reaction(bot, karma_r)

    @commands.cooldown (rate=2, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def uptime(self, ctx):
        """Bot uptime"""
        now = datetime.datetime.now().replace(microsecond=0)
        delta = now - boottime

        embed = self._getEmbed(ctx)
        embed.add_field(name="Boot", value=str(boottime), inline=False)
        embed.add_field(name="Uptime", value=str(delta), inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)

    @commands.cooldown (rate=2, per=60.0, type=commands.BucketType.user)
    @commands.command(aliases=["goddess"])
    async def god(self, ctx):
        """Display information about bot functions"""
        embed = self.reaction.make_embed(1)
        msg = await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx)
        await msg.add_reaction("◀")
        await msg.add_reaction("▶")

    
    @commands.command()
    async def help (self, ctx, pin: str = None):
        """Display information about bot functions (beta)

        This should replace current `?god`/`?goddess` commands in the future
        Instead of reading help from file it is taking dostrings inside the code
        """
        #TODO Add crolling
        pin = self.parseArg(pin)
        t = self._getEmbedTitle(ctx)
        if pin is not None and pin:
            t = "📌 " + t
        embed = discord.Embed(color=config.color,
            title=t, description=ctx.command.short_doc)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        cogs = self.bot.cogs
        for cog in cogs:
            cog = self.bot.get_cog(cog)
            if not isinstance(cog, rubbercog.Rubbercog) or not cog.visible:
                # Do not display hidden or non-Rubbercog objects
                continue
            embed.add_field(inline=False,
                name=cog.qualified_name,
                value=cog.description if cog.description else "_No description available_")

        msg = await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)

def setup(bot):
    bot.add_cog(Base(bot))
