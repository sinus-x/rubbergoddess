import asyncio

import discord
from discord.ext import commands

from core import check, rubbercog
from core.config import config
from repository.subject_repo import SubjectRepository

repo_s = SubjectRepository()

"""
This file should replace react-to-role part of reaction.py in the future.

As it is still in development, we're keeping it in separate branch.
"""


class Roles(rubbercog.Rubbercog):
    """Edit the roles"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.guild_only()
    @commands.check(check.is_native)
    @commands.group(name="subject")
    async def subject(self, ctx):
        """Add or remove subject"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @subject.command(name="add")
    async def subject_add(self, ctx, *, subjects: str):
        """Add subject

        subjects: Space separated subject codes
        """
        # check if all subjects are in database
        shortcuts = discord.utils.escape_markdown(subjects).lower().replace("@", "").split(" ")
        for shortcut in shortcuts:
            if not await self.subject_in_database(ctx=ctx, shortcut=shortcut):
                return

        # edit permissions
        added = False
        for shortcut in shortcuts:
            channel = await self.subject_in_channels(ctx=ctx, shortcut=shortcut)
            if not isinstance(channel, discord.TextChannel):
                return

            await self._add_subject(shortcut=shortcut, ctx=ctx, channel=channel)
            added = True

        # add checkmark, wait and delete message
        if added:
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(config.get("delay", "success"))

        await self.deleteCommand(ctx)

    @subject.command(name="remove")
    async def subject_remove(self, ctx, *, subjects: str):
        """Remove subject

        subjects: Space separated subject codes
        """
        shortcuts = discord.utils.escape_markdown(subjects).lower().replace("@", "").split(" ")
        for shortcut in shortcuts:
            if not await self.subject_in_database(ctx=ctx, shortcut=shortcut):
                return

        # edit permissions
        added = False
        for shortcut in shortcuts:
            channel = await self.subject_in_channels(ctx=ctx, shortcut=shortcut)
            if not isinstance(channel, discord.TextChannel):
                return

            await self._remove_subject(shortcut=shortcut, ctx=ctx, channel=channel)
            added = True

        # add checkmark, wait and delete message
        if added:
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(config.get("delay", "success"))

        await self.deleteCommand(ctx)

    async def subject_in_database(self, *, ctx: commands.Context, shortcut: str):
        """Display error and delete message if shortcut is not valid subject"""
        if repo_s.get(shortcut) is None:
            await ctx.send(
                f"**{shortcut}** is not a subject", delete_after=config.get("delay", "error"),
            )
            await ctx.message.add_reaction("❎")
            await asyncio.sleep(config.get("delay", "error"))
            await self.deleteCommand(ctx)
            return False
        return True

    async def subject_in_channels(self, *, ctx: commands.Context, shortcut: str):
        """Send error if shortcut is not valid channel"""
        channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)
        if channel is None:
            await ctx.send(
                f"Channel for **{shortcut}** does not exist",
                delete_after=config.get("delay", "error"),
            )
            return False
        return channel

    async def _add_subject(
        self, *, ctx: commands.Context, shortcut: str, channel: discord.TextChannel = None
    ):
        """Add subject channel"""
        if channel is None and ctx is None:
            return self.console.error("Roles:_add_subject", "No channel to apply the overrides to")
        elif channel is None:
            channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)

        await channel.set_permissions(ctx.author, view_channel=True, reason="?subject")

        # try to add teacher subject
        shortcut = shortcut + config.get("channels", "teacher suffix")
        channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)
        if channel is not None:
            await channel.set_permissions(ctx.author, view_channel=True, reason="?subject")

    async def _remove_subject(
        self, *, ctx: commands.Context, shortcut: str, channel: discord.TextChannel = None
    ):
        """Remove subject channel"""
        if channel is None and ctx is None:
            return self.console.error(
                "Roles:_remove_subject", "No channel to apply the overrides to"
            )
        elif channel is None:
            channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)

        await channel.set_permissions(ctx.author, overwrite=None, reason="?subject")

        # try to remove teacher subject
        shortcut = shortcut + config.get("channels", "teacher suffix")
        channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)
        if channel is not None:
            await channel.set_permissions(ctx.author, overwrite=None, reason="?subject")


def setup(bot):
    bot.add_cog(Roles(bot))
