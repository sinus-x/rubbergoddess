import random
import asyncio

import discord
from discord.ext import commands

from core.config import config
from core.text import text
from core import check, rubbercog, utils

class Voice(rubbercog.Rubbercog):
    """Manage channels"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = True
        self.locked = []

    def getVoiceChannel(self, ctx: commands.Context):
        return ctx.author.voice.channel

    @commands.check(check.is_in_voice)
    @commands.bot_has_permissions(manage_channels=True, manage_messages=True)
    @commands.group(name="voice")
    async def voice(self, ctx: commands.Context):
        """Manage your voice channel"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            return

    @voice.command(name="lock", aliases=["close"])
    async def voice_lock(self, ctx: commands.Context):
        """Make current voice channel invisible"""
        await self.throwNotification(ctx, text.get("error", "not implemented"))
        return

    @voice.command(name="unlock", aliases=["open"])
    async def voice_unlock(self, ctx: commands.Context):
        """Make current voice channel visible"""
        await self.throwNotification(ctx, text.get("error", "not implemented"))
        return

    @voice.command(name="rename")
    async def voice_rename(self, ctx: commands.Context, *args):
        """Rename current voice channel"""
        name = ' '.join(args)
        if len(name) < 0:
            await ctx.send("Enter at least one valid character.")
            return
        if len(name) > 24:
            await ctx.send("Name too long.")
            return

        channel = self.getVoiceChannel(ctx)
        await channel.edit(name=name)

    @commands.Cog.listener()
    async def on_voice_state_update (self, user: discord.Member, beforeState: discord.VoiceState,
                                           afterState: discord.VoiceState):
        """Detect changes in voice channels"""
        # Get voice objects
        before = beforeState.channel
        after  = afterState.channel

        # Do not act if no one has joined or left, or the action is on another server
        if before == after or (before is None and after is None) \
        or before not in self.getGuild().channels and after not in self.getGuild().channels:
            return

        voices = self.getGuild().get_channel(config.channel_voices)
        nomic  = self.getGuild().get_channel(config.channel_nomic)

        # alter access to the nomic text channel
        if before is None:
            await nomic.set_permissions(user, read_messages=True)
        elif after is None:
            await nomic.set_permissions(user, overwrite=None)

        await self.voiceCleanup()

    async def setVoiceName(self, channel: discord.VoiceChannel):
        """Set voice channel name"""
        if len(channel.members) == 0:
            await channel.edit(name="Empty")
            return

        color = ["Red", "Green", "Blue", "Black", "White", "Pink", "Orange"]
        noun = ["cat", "dog", "elephant", "horse", "mouse", "fish",
                "octopus", "cockroach", "butterfly", "owl", "fox", "tiger",
                "bear", "sheep", "duck", "panda", "rabbit", "wolf"]

        name = "{} {}".format(random.choice(color), random.choice(noun))
        await channel.edit(name=name)

    async def voiceCleanup(self):
        """Clear nomic"""
        voices = self.getGuild().get_channel(config.channel_voices)
        nomic = self.getGuild().get_channel(config.channel_nomic)

        empty = None
        # Rename populated 'Empty' channels. Get last empty channel
        for v in voices.voice_channels:
            if len(v.members) == 0:
                empty = v
            elif len(v.members) > 0 and v.name == 'Empty':
                await self.setVoiceName(v)

        # Remove all previous 'Empty' channels
        for v in voices.voice_channels:
            if len(v.members) == 0 and v is not empty:
                await v.delete()

        # Move 'Empty' to end
        if empty:
            await empty.edit(name='Empty', position=len(voices.channels))
        else:
            await self.getGuild().create_voice_channel(name='Empty', category=voices)

        # Clear nomic if no one is left
        if len(voices.voice_channels) == 1:
            await nomic.purge()

def setup(bot):
    bot.add_cog(Voice(bot))
