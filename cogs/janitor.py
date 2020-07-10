import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text


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

        await utils.delete(ctx)

    @commands.guild_only()
    @commands.check(check.is_elevated)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def purge(self, ctx, limit: int, pinMode: str = "pinSkip"):
        """Delete messages from current text channel

        limit: how many messages should be deleted
        mode: pinSkip (default) | pinStop | pinIgnore
        """
        if pinMode not in ("pinSkip", "pinStop", "pinIgnore"):
            return await ctx.send_help(ctx.invoked_with)

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

        await self.event.sudo(
            ctx.author, ctx.channel, f"Purged {total} posts in {ctx.channel}",
        )

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

        await self.event.sudo(ctx.author, ctx.channel, f"Teacher channel {ch.name}")


def setup(bot):
    bot.add_cog(Janitor(bot))
