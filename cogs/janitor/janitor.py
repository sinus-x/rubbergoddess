import time

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import acl, rubbercog
from core.config import config


class Janitor(rubbercog.Rubbercog):
    """Manage users, roles and channels"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("janitor")

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(acl.check)
    @commands.command()
    async def hoarders(self, ctx: commands.Context, warn: str = None):
        """Check for users with multiple programme roles

        warn: Optional. Use "warn" string to send warnings, else just list the users
        """
        warn = warn == "warn"

        hoarders = []
        limit_top = discord.utils.get(self.getGuild().roles, name="---PROGRAMMES")
        limit_bottom = discord.utils.get(self.getGuild().roles, name="---INTERESTS")

        for member in self.getGuild().members:
            prog = []
            for role in member.roles:
                if role < limit_top and role > limit_bottom:
                    prog.append(role.name)
            if len(prog) > 1:
                hoarders.append([member, prog])

        if len(hoarders) == 0:
            return await ctx.send(self.text.get("no_hoarders"))

        embed = self.embed(ctx=ctx, title=self.text.get("embed", "title"))
        if warn:
            msg = await ctx.send(self.text.get("sending", num=1, all=len(hoarders)))

        for num, (hoarder, progs) in enumerate(hoarders):
            # fmt: off
            embed.add_field(
                name=self.text.get("embed", "user"),
                value=f"**{self.sanitise(hoarder.name)}** ({hoarder.id})",
            )
            embed.add_field(
                name=self.text.get("embed", "status"),
                value=hoarder.status
            )
            embed.add_field(
                name=self.text.get("embed", "programmes"),
                value=", ".join(progs),
                inline=False,
            )
            if warn:
                if num % 5 == 0:
                    await msg.edit(content=self.text.get("sending", num=num, all=len(hoarders)))
                await hoarder.send(self.text.get("warning", guild=self.getGuild().name))
            if num % 8 == 0:
                # There's a limit of 25 fields per embed
                await ctx.send(embed=embed)
                embed = embed.clear_fields()
            # fmt: on
        if warn:
            await msg.edit(content=self.text.get("sent", num=len(hoarders)))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.check(acl.check)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def purge(self, ctx, limit: int, pinMode: str = "pinSkip"):
        """Delete messages from current text channel

        limit: how many messages should be deleted
        mode: pinSkip (default) | pinStop | pinIgnore
        """
        if pinMode not in ("pinSkip", "pinStop", "pinIgnore"):
            return await ctx.send_help(ctx.invoked_with)

        now = time.monotonic()
        messages = await ctx.channel.history(limit=limit).flatten()

        total = 0
        for message in messages:
            if message.pinned and pinMode == "pinStop":
                break
            elif message.pinned and pinMode == "pinSkip":
                continue

            try:
                await message.delete()
                total += 1
            except discord.HTTPException:
                pass

        delta = str(int(time.monotonic() - now))
        await self.event.sudo(ctx, f"Purged {total} posts in {delta}s.")

    @commands.check(acl.check)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.command(name="teacher_channel", aliases=["teacher-channel"])
    async def teacher_channel(self, ctx, channel: discord.TextChannel):
        """Create subject channel will be visible for the subject's teacher, too

        channel: Subject channel to be duplicated
        """
        if channel.name not in config.subjects:
            return await self.output.error(
                ctx, self.text.get("not_subject", channel=channel.mention)
            )

        ch = await channel.clone(name=channel.name + config.get("channels", "teacher suffix"))
        await ch.edit(position=channel.position + 1)
        await ctx.send(self.text.get("teacher_channel", channel=channel.mention))

        await self.event.sudo(ctx, f"Teacher channel {ch.name}")


def setup(bot):
    bot.add_cog(Janitor(bot))
