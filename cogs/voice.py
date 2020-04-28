import random

import discord
from discord.ext import commands

from core import check, config, rubbercog, text, utils

class Voice(rubbercog.Rubbercog):
    """Manage channels"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = True
        self.channels = {}
        self.locked = []

    @commands.check(check.is_in_voice)
    @commands.bot_has_permissions(manage_channels=True, manage_messages=True)
    @commands.group(name="voice")
    async def voice(self, ctx: commands.Context):
        """Manage your voice channel"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            return

    @voice.command(name="lock")
    async def voice_lock(self, ctx: commands.Context):
        """Make current voice channel invisible"""
        await self.throwNotification(ctx, text.get("error", "not implemented"))
        return

    @voice.command(name="unlock")
    async def voice_unlock(self, ctx: commands.Context):
        """Make current voice channel visible"""
        await self.throwNotification(ctx, text.get("error", "not implemented"))
        return

    @commands.Cog.listener()
    async def on_voice_state_update (self, user: discord.Member, beforeState: discord.VoiceState,
                                           afterState: discord.VoiceState):
        """Detect changes in voice channels"""
        # Get voice objects
        before = beforeState.channel
        after  = afterState.channel
        voices = self.getGuild().get_channel(config.channel_voices)
        nomic  = self.getGuild().get_channel(config.channel_nomic)

        # Do not act if no one has joined or left
        if before == after or (before is None and after is None):
            return

        if before is None: # user joined
            await self.setVoiceName(after)
            if len(after.members) == 1:
                # create another empty channel
                ch = await self.getGuild().create_voice_channel(".", category=voices)
                await self.setVoiceName(ch)
            # show them "no mic" channel
            await nomic.set_permissions(user, read_messages=True)

        elif after is None: # user left
            if len(before.members) == 0 and len(voices.voice_channels) > 1:
                await before.delete()
            else:
                await self.setVoiceName(before)
            await self.voiceCleanup()
            await nomic.set_permissions(user, overwrite=None)
        else:
            await self.setVoiceName(before)
            await self.setVoiceName(after)


    async def setVoiceName(self, channel: discord.VoiceChannel):
        """Set voice channel name"""
        if len(channel.members) == 0:
            await channel.edit(name="Empty")
            return

        size = ["Big", "Small", "Tiny", "Huge"]
        color = ["red", "green", "blue", "black", "white", "pink", "orange"]
        noun = ["cat", "dog", "elephant", "horse", "mouse"]

        name = "{} {} {}".format(
            random.choice(size), random.choice(color), random.choice(noun))
        await channel.edit(name=name)

    async def voiceCleanup(self):
        """Clear nomic"""
        voices = self.getGuild().get_channel(config.channel_voices)
        nomic = self.getGuild().get_channel(config.channel_nomic)

        empty = True
        for voice in voices.voice_channels:
            if len(voice.members) > 0:
                empty = False
                break

        if empty:
            await nomic.purge()


def setup(bot):
    bot.add_cog(Voice(bot))
