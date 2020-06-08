import discord
from discord.ext import commands

from core.config import config
from core.text import text
from core import check, rubbercog


class Janitor(rubbercog.Rubbercog):
    """Manage channels"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(check.is_in_modroom)
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def hoarders(self, ctx: commands.Context, warn: str = None):
        """Check for users with multiple programme roles

        warn: Optional. Use "warn" string to send warnings, else just list the users
        """
        if warn == "warn":
            warn = True
        else:
            warn = False

        hoarders = []
        for member in self.getGuild().members:
            prog = []
            for role in member.roles:
                if role < discord.utils.get(
                    self.getGuild().roles, name="---FEKT"
                ) and role > discord.utils.get(self.getGuild().roles, name="---"):
                    prog.append(role.name)
            if len(prog) > 1:
                hoarders.append([member, prog])

        if len(hoarders) == 0:
            await ctx.send(text.get("janitor", "no hoarders"))
        else:
            all = len(hoarders)
            if warn:
                msg = await ctx.send("Odesílání zprávy 1/{all}.".format(all=all))
            embed = discord.Embed(title="Programme hoarders", color=config.color)
            for num, (hoarder, progs) in enumerate(hoarders, start=1):
                embed.add_field(
                    name="User",
                    value=f"**{discord.utils.escape_markdown(hoarder.name)}** ({hoarder.id})",
                )
                embed.add_field(name="Status", value=hoarder.status)
                embed.add_field(name="Programmes", value=", ".join(progs), inline=False)
                if warn:
                    if num % 5 == 0:  # Do not stress the API too much
                        await msg.edit(
                            content="Odesílání zprávy {num}/{all}.".format(num=num, all=all)
                        )
                    await hoarder.send(
                        text.fill("janitor", "hoarding warning", guild=self.getGuild().name)
                    )
                if num % 8 == 0:  # Can't have more than 25 fields in an embed
                    await ctx.channel.send(embed=embed, delete_after=config.delay_embed)
                    embed = discord.Embed(title="Programme hoarders", color=config.color)
            if warn and num % 5 != 0:
                await msg.edit(content="Odesílání zprávy {num}/{all}.".format(num=num, all=all))
            await ctx.channel.send(embed=embed, delete_after=config.delay_embed)

        await self.deleteCommand(ctx)

    @commands.check(check.is_elevated)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def purge(self, ctx, limit=None, pinMode="pinSkip"):
        """Delete messages from current text channel

        limit: how many messages should be deleted
        mode: pinSkip (default) | pinStop | pinIgnore
        """
        channel = ctx.channel
        if not isinstance(channel, discord.TextChannel):
            return await self.throwHelp(ctx)

        if limit is None:
            return await self.throwHelp(ctx)
        else:
            try:
                limit = int(limit) + 1
            except ValueError:
                self.throwHelp(ctx)

        if limit:
            msgs = channel.history(limit=limit)
        else:
            msgs = channel.history()
        ctr_del = 0
        ctr_skip = 0
        ctr_pin = 0
        ctr_err = 0
        async for m in msgs:
            if m.pinned and pinMode == "pinStop":
                break
            elif m.pinned and pinMode == "pinSkip":
                ctr_skip += 1
                continue
            elif m.pinned and pinMode == "pinIgnore":
                ctr_pin += 1
            try:
                await m.delete()
                ctr_del += 1
            except discord.HTTPException:
                ctr_err += 1

        embed = discord.Embed(title="?purge", color=config.color)
        embed.add_field(
            name="Settings",
            value="Channel **{}**, limit **{}**, pinMode **{}**".format(
                channel, limit - 1 if limit else "none", pinMode if pinMode else "ignore"
            ),
        )
        embed.add_field(
            name="Result",
            value="**{deleted}** removed (**{pinned}** were pinned), **{skipped}** skipped.\n"
            "**{err}** errors occured.".format(
                deleted=ctr_del - 1 + ctr_pin, skipped=ctr_skip, pinned=ctr_pin, err=ctr_err
            ),
        )
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        channel = self.getGuild().get_channel(config.channel_botlog)
        await channel.send(embed=embed)

    @commands.check(check.is_mod)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.command(name="teacher_channel", aliases=["teacher-channel"])
    async def teacher_channel(self, ctx, channel: discord.TextChannel):
        """Create subject channel will be visible for the subject's teacher, too

        channel: Subject channel to be duplicated
        """
        if channel.name not in config.subjects:
            return await self.output.error(
                ctx, text.fill("janitor", "teacher not subject", channel=channel.mention)
            )

        ch = await channel.clone(name=channel.name + config.get("channels", "teacher suffix"))
        await ch.edit(position=channel.position + 1)
        await ctx.send(f"Created channel {ch.mention}")


def setup(bot):
    bot.add_cog(Janitor(bot))
