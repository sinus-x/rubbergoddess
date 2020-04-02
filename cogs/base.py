import datetime
import traceback

import discord
from discord.ext import commands

import utils
from config.config import Config as config
from config.messages import Messages as messages
from logic import rng
from features import reaction
from repository import karma_repo
from cogs import room_check, errors

rng = rng.Rng()
karma_r = karma_repo.KarmaRepository()

boottime = datetime.datetime.now().replace(microsecond=0)


class Base (commands.Cog):
    """About-bot cog"""
    def __init__(self, bot):
        self.bot = bot
        self.reaction = reaction.Reaction(bot, karma_r)
        self.check = room_check.RoomCheck(bot)
        self.errors = errors.Errors(bot)

    @commands.cooldown (rate=2, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def uptime(self, ctx):
        """Bot uptime"""
        now = datetime.datetime.now().replace(microsecond=0)
        delta = now - boottime

        t = self.errors._getEmbedTitle(ctx)
        embed = discord.Embed(color=config.color, title=t, description=ctx.command.short_doc)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Boot", value=str(boottime), inline=False)
        embed.add_field(name="Uptime", value=str(delta), inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_message)
        await self.errors._tryDelete(ctx, now=True)

    @commands.cooldown (rate=2, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def week(self, ctx):
        """See if the current week is odd or even"""
        await ctx.send(rng.week())

    @commands.cooldown (rate=2, per=60.0, type=commands.BucketType.user)
    @commands.command(aliases=["goddess"])
    async def god(self, ctx):
        """Display information about bot functions"""
        embed = self.reaction.make_embed(1)

        channel = await self.check.get_room(ctx.message)
        if channel is not None and channel.id != config.bot_room:
            try:
                msg = await ctx.author.send(embed=embed)
                await ctx.message.delete()
            except discord.errors.Forbidden:
                return
        else:
            msg = await ctx.send(embed=embed, delete_after=config.delay_embed)
            await ctx.message.delete(delay=config.delay_message)
        await msg.add_reaction("◀")
        await msg.add_reaction("▶")

    @commands.command()
    async def help (self, ctx, pin: str = None):
        """Display information about bot functions (beta)

        This should replace current `?god`/`?goddess` commands in the future
        Instead of reading help from file it is taking dostrings inside the code
        """
        pin = self.errors._parsePin(pin)
        t = self.errors._getEmbedTitle(ctx)
        if pin is not None and pin:
            t = "📌 " + t
        embed = discord.Embed(color=config.color,
            title=t, description=ctx.command.short_doc)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        cogs = self.bot.cogs
        for cog in cogs:
            cog = self.bot.get_cog(cog)
            embed.add_field(
                name=cog.qualified_name,
                value=cog.description if cog.description else "_No description available_")


        msg = await ctx.send(embed=embed, delete_after=config.delay_embed)
        await msg.add_reaction("◀")
        await msg.add_reaction("▶")
        await self.errors._tryDelete(ctx, now=True)

def setup(bot):
    bot.add_cog(Base(bot))
