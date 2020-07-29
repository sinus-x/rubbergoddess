import discord
from discord.ext import commands

from cogs.resource import CogText
from core import check, rubbercog, utils
from repository import seeking_repo

repo_s = seeking_repo.SeekingRepository()


class Seeking(rubbercog.Rubbercog):
    """Look for... stuff"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("seeking")

    @commands.guild_only()
    @commands.check(check.is_verified)
    @commands.group(name="hledam", aliases=["hledám", "seeking"])
    async def seeking(self, ctx):
        """List items for current channel"""
        if ctx.invoked_subcommand is not None:
            return

        embed = self.embed(ctx=ctx, title="Hledám")
        items = repo_s.getAll(ctx.channel.id)

        if items is not None:
            template = self.text.get("embed", "template")
            for item in items:
                member = ctx.guild.get_member(item.user_id)
                name = (
                    self.sanitise(member.display_name)
                    if hasattr(member, "display_name")
                    else self.text.get("embed", "no_user")
                )
                embed.add_field(
                    name=template.format(
                        id=item.id, name=name, timestamp=item.timestamp.strftime("%Y-%m-%d %H:%M")
                    ),
                    value=item.text,
                    inline=False,
                )
        else:
            embed.add_field(name="\u200b", value=self.text.get("embed", "no_items"))
        await ctx.send(embed=embed)

    @seeking.command(name="add")
    async def seeking_add(self, ctx, *, text: str):
        """Announce that you're seeking something"""
        if len(text) > 140:
            return await ctx.send(self.text.get("add", "too_long"))

        repo_s.add(user_id=ctx.author.id, channel_id=ctx.channel.id, text=text)
        await ctx.send(self.text.get("add", "ok"))

    @seeking.command(name="remove")
    async def seeking_remove(self, ctx, id: int):
        """Remove your item"""
        item = repo_s.get(item_id=id)

        if item is None:
            return await ctx.send(self.text.get("remove", "not_found"))

        repo_s.delete(id)
        await ctx.send(self.text.get("remove", "ok"))
