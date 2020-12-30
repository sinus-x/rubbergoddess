import datetime

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import rubbercog, utils
from core.config import config

boottime = datetime.datetime.now().replace(microsecond=0)


class Base(rubbercog.Rubbercog):
    """About"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

        self.config = CogConfig("base")
        self.text = CogText("base")

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

        for reaction in message.reactions:
            if reaction.emoji != "📌":
                continue

            if message.pinned:
                return await reaction.clear()

            if reaction.count < self.config.get("pins"):
                return

            users = await reaction.users().flatten()
            user_names = ", ".join([str(user) for user in users])
            log_embed = self.embed(title=self.text.get("pinned"), description=user_names)
            if len(message.content):
                value = utils.id_to_datetime(message.id).strftime("%Y-%m-%d %H:%M:%S")
                log_embed.add_field(name=str(message.author), value=value)
            url_text = self.text.get(
                "link text",
                channel=channel.name,
                guild=channel.guild.name,
            )
            if len(message.content):
                log_embed.add_field(
                    name=self.text.get("content"),
                    value=message.content[:1024],
                    inline=False,
                )
            if len(message.content) >= 1024:
                log_embed.add_field(
                    name="\u200b",
                    value=message.content[1024:],
                    inline=False,
                )
            if len(message.attachments):
                log_embed.add_field(
                    name=self.text.get("content"),
                    value=self.text.get("attachments", count=len(message.attachments)),
                    inline=False,
                )
            log_embed.add_field(
                name=self.text.get("link"),
                value=f"[{url_text}]({message.jump_url})",
                inline=False,
            )

            try:
                await message.pin()
            except discord.HTTPException as e:
                await self.event.user(channel, "Could not pin message.", e)
                error_embed = self.embed(
                    title=self.text.get("pin error"),
                    description=user_names,
                    url=message.jump_url,
                )
                await message.channel.send(embed=error_embed)
                return

            event_channel = self.bot.get_channel(config.get("channels", "events"))
            await event_channel.send(embed=log_embed)

            await reaction.clear()
            await message.add_reaction("📍")
