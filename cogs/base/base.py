import datetime

import discord
from discord.ext import commands

from cogs.resource import CogConfig
from core import rubbercog
from core.config import config

boottime = datetime.datetime.now().replace(microsecond=0)


class Base(rubbercog.Rubbercog):
    """About"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

        self.config = CogConfig("base")

    ##
    ## Commands
    ##

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def uptime(self, ctx):
        """Bot uptime"""
        now = datetime.datetime.now().replace(microsecond=0)
        delta = now - boottime

        embed = self.embed(ctx=ctx)
        embed.add_field(name="Boot", value=str(boottime), inline=False)
        embed.add_field(name="Uptime", value=str(delta), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Bot latency"""
        await ctx.send("pong: **{:.2f} s**".format(self.bot.latency))

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Pinning functionality"""
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        if payload.emoji.is_custom_emoji() or payload.emoji.name != "📌":
            return

        if message.pinned:
            # TODO Remove the reaction
            return

        for reaction in message.reactions:
            if reaction.emoji != "📌":
                continue

            if message.pinned:
                return await reaction.clear()

            if reaction.count < self.config.get("pins"):
                return

            users = await reaction.users().flatten()
            user_names = ", ".join([str(user) for user in users])

            embed = self.embed(title="📌 " + message.channel.name, description=user_names)
            if len(message.content):
                value = message.content[:200] + ("…" if len(message.content) > 200 else "")
                embed.add_field(name=str(message.author), value=value)
            embed.add_field(name="URL", value=message.jump_url, inline=False)

            channel = self.bot.get_channel(config.get("channels", "events"))
            await channel.send(embed=embed)
            try:
                await message.pin()
                await reaction.clear()
            except discord.HTTPException:
                break
