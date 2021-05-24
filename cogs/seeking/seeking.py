import discord
from discord.ext import commands

from cogs.resource import CogText
from core import check, rubbercog, utils
from core.config import config
from repository import seeking_repo

repo_s = seeking_repo.SeekingRepository()


class Seeking(rubbercog.Rubbercog):
    """Look for... stuff"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("seeking")

    @commands.guild_only()
    @commands.check(check.is_verified)
    @commands.group(name="seeking", aliases=["hledám", "hledam"])
    async def seeking(self, ctx):
        """List items for current channel"""
        if ctx.invoked_subcommand is not None:
            return

        embed = self.embed(ctx=ctx, title=self.text.get("embed", "title"))
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
                try:
                    message = await ctx.channel.fetch_message(item.message_id)
                except discord.NotFound:
                    message = None
                if message:
                    text = item.text + f" | [link]({message.jump_url})"
                else:
                    text = item.text
                embed.add_field(
                    name=template.format(
                        id=item.id,
                        name=name,
                        timestamp=utils.id_to_datetime(item.message_id).strftime("%Y-%m-%d %H:%M"),
                    ),
                    value=text,
                    inline=False,
                )
        else:
            embed.add_field(name="\u200b", value=self.text.get("embed", "no_items"))
        await ctx.send(embed=embed)

    @seeking.command(name="add")
    async def seeking_add(self, ctx, *, text: str):
        """Announce that you're seeking something in under 140 characters

        Arguments
        ---------
        text: Any text in the character limit
        """
        if len(text) > 140:
            return await ctx.reply(self.text.get("add", "too_long"))

        repo_s.add(
            user_id=ctx.author.id, message_id=ctx.message.id, channel_id=ctx.channel.id, text=text
        )
        await ctx.reply(self.text.get("add", "ok"))

    @seeking.command(name="remove")
    async def seeking_remove(self, ctx, *, ids: str):
        """Remove your item

        Arguments
        ---------
        ids: space separated integers
        """
        ids = ids.split(" ")

        rejected = []

        items = []
        for item in ids:
            if not len(ids):
                continue

            try:
                items.append(int(item))
            except Exception:
                rejected.append(item)

        for item_id in items:
            item = repo_s.get(item_id)
            if item is None:
                rejected.append(item_id)
                continue

            if item.user_id != ctx.author.id and ctx.author.id != config.admin_id:
                rejected.append(item_id)
                continue

            repo_s.delete(item_id)

        await ctx.reply(self.text.get("remove", "done"))
        if len(rejected):
            await ctx.send(
                self.text.get(
                    "remove",
                    "rejected",
                    rejected=", ".join(f"`{self.sanitise(str(x))}`" for x in rejected),
                )[:2000]
            )
