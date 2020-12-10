import random

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core.config import config
from core import check, rubbercog, utils


class Voice(rubbercog.Rubbercog):
    """Manage voice channels"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("voice")
        self.text = CogText("voice")

        self.locked = []

    ##
    ## Commands
    ##

    @commands.guild_only()
    @commands.check(check.is_in_voice)
    @commands.bot_has_permissions(manage_channels=True, manage_messages=True)
    @commands.group(name="voice")
    async def voice(self, ctx):
        """Manage voice channels"""
        await utils.send_help(ctx)

    @voice.command(name="lock", aliases=["close"])
    async def voice_lock(self, ctx):
        """Make current voice channel invisible"""
        voice = self.users_voice_channel(ctx)
        # Lock
        await voice.set_permissions(self.getVerifyRole(), overwrite=None)
        if ctx.channel.id not in self.locked:
            self.locked.append(ctx.channel.id)
        # Report
        await ctx.send(self.text.get("locked", name=self.sanitise(voice.name)), delete_after=10)
        await utils.delete(ctx.message)
        await self.event.user(ctx, f"Channel locked: **{voice.name}**.")

    @voice.command(name="unlock", aliases=["open"])
    async def voice_unlock(self, ctx):
        """Make current voice channel visible"""
        voice = self.users_voice_channel(ctx)
        # Unlock
        await voice.set_permissions(self.getVerifyRole(), view_channel=True)
        if ctx.channel.id in self.locked:
            self.locked.remove(ctx.channel.id)
        # Report
        await ctx.send(self.text.get("unlocked", name=self.sanitise(voice.name)), delete_after=10)
        await utils.delete(ctx.message)
        await self.event.user(ctx, f"Channel unlocked: **{voice.name}**.")

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, beforeState, afterState):
        """Detect changes in voice channels"""

        # get voice objects
        before = beforeState.channel
        after = afterState.channel

        # Do not act if no one has left or joined
        if before == after or (before is None and after is None):
            return
        # Do not act if the action is not on main guild
        if before not in self.getGuild().channels and after not in self.getGuild().channels:
            return

        # Get voice-no-mic channel
        nomic = self.getGuild().get_channel(config.channel_nomic)

        # Manage channel overwrites
        if before is None:
            # User joined
            await nomic.set_permissions(member, view_channel=True)
            try:
                await after.set_permissions(member, view_channel=True)
            except Exception as e:
                await self.console.warning(member, f"Could not add overwrite to {after}.", e)

            # Send welcome message
            await nomic.send(
                self.text.get(
                    "welcome", nickname=self.sanitise(member.display_name), prefix=config.prefix
                ),
                delete_after=30,
            )

        elif after is None:
            # User left
            await nomic.set_permissions(member, overwrite=None)
            try:
                await before.set_permissions(member, overwrite=None)
            except Exception as e:
                await self.console.warning(member, f"Could not remove overwrite from {before}.", e)

        else:
            # User moved
            try:
                await before.set_permissions(member, overwrite=None)
            except Exception as e:
                await self.console.warning(member, f"Could not remove overwrite from {before}.", e)
            try:
                await after.set_permissions(member, view_channel=True)
            except Exception as e:
                await self.console.warning(member, f"Could not add overwrite to {before}.", e)

        # Do cleanup
        await self.cleanup_channels()

    ##
    ## Logic
    ##

    async def cleanup_channels(self):
        """Remove empty voice channels"""
        category = self.getGuild().get_channel(config.channel_voices)
        nomic = self.getGuild().get_channel(config.channel_nomic)

        empty = []
        for voice in category.voice_channels:
            if len(voice.members) == 0:
                empty.append(voice)

        if len(empty) == 0:
            # Need to add one
            voice = await self.getGuild().create_voice_channel(
                name=self.gen_channel_name(), category=category
            )
            await voice.set_permissions(self.getVerifyRole(), view_channel=True)
            return

        # Delete all except the last one
        for voice in empty[:-1]:
            try:
                await voice.delete()
            except discord.NotFound as e:
                await self.console.warning("Voice cleanup", f"Channel {voice} not found.", e)

        # Make sure the empty is writable
        await empty[-1].set_permissions(self.getVerifyRole(), view_channel=True)

        if len(category.voice_channels) == 1:
            # No one inside, can safely wipe no-mic channel
            await nomic.purge()
            # Just to make sure
            self.locked = []

    ##
    ## Helper functions
    ##

    def users_voice_channel(self, ctx: commands.Context):
        return ctx.author.voice.channel

    def gen_channel_name(self) -> str:
        adjectives = self.config.get("adjectives")
        nouns = self.config.get("nouns")
        return "{} {}".format(random.choice(adjectives), random.choice(nouns))
