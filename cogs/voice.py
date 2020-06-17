import random

import discord
from discord.ext import commands

from core.config import config
from core.text import text
from core import check, rubbercog, utils


class Voice(rubbercog.Rubbercog):
    """Manage voice channels"""

    def __init__(self, bot):
        super().__init__(bot)
        self.lock = text.get("voice", "lock")
        self.locked = []

    def getVoiceChannel(self, ctx: commands.Context):
        return ctx.author.voice.channel

    @commands.check(check.is_in_voice)
    @commands.bot_has_permissions(manage_channels=True, manage_messages=True)
    @commands.group(name="voice")
    async def voice(self, ctx: commands.Context):
        """Manage your voice channel"""
        await utils.send_help(ctx)

    @voice.command(name="lock", aliases=["close"])
    async def voice_lock(self, ctx: commands.Context):
        """Make current voice channel invisible"""
        await utils.delete(ctx)
        v = self.getVoiceChannel(ctx)
        if v.id in self.locked:
            await ctx.send(
                delete_after=config.delay_embed,
                content=text.fill("voice", "lock error", user=ctx.author),
            )
            return
        await v.set_permissions(self.getVerifyRole(), overwrite=None)
        await v.edit(name=v.name + " " + self.lock)
        self.locked.append(v.id)

    @voice.command(name="unlock", aliases=["open"])
    async def voice_unlock(self, ctx: commands.Context):
        """Make current voice channel visible"""
        await utils.delete(ctx)
        v = self.getVoiceChannel(ctx)
        if v.id not in self.locked:
            await ctx.send(
                delete_after=config.delay_embed,
                content=text.fill("voice", "unlock error", user=ctx.author),
            )
            return
        await v.set_permissions(self.getVerifyRole(), view_channel=True)
        await v.edit(name=v.name.replace(" " + self.lock, ""))
        self.locked.remove(v.id)

    @voice.command(name="rename")
    async def voice_rename(self, ctx: commands.Context, *args):
        """Rename current voice channel"""
        await utils.delete(ctx)
        name = " ".join(args)
        if len(name) <= 0:
            await ctx.send(
                delete_after=config.delay_embed,
                content=text.fill("voice", "rename empty", user=ctx.author),
            )
            return
        if len(name) > 25:
            await ctx.send(
                delete_after=config.delay_embed,
                content=text.fill("voice", "rename long", user=ctx.author),
            )
            return

        v = self.getVoiceChannel(ctx)
        name = name.replace(" " + self.lock, "").replace(self.lock, "")
        if v.id in self.locked:
            name = name + " " + self.lock
        await v.edit(name=name)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, user: discord.Member, beforeState: discord.VoiceState, afterState: discord.VoiceState
    ):
        """Detect changes in voice channels"""
        # Get voice objects
        before = beforeState.channel
        after = afterState.channel

        # Do not act if no one has joined or left, or the action is on another server
        if (
            before == after
            or (before is None and after is None)
            or before not in self.getGuild().channels
            and after not in self.getGuild().channels
        ):
            return

        nomic = self.getGuild().get_channel(config.channel_nomic)

        # alter access to the channels
        if before is None:
            await after.set_permissions(user, view_channel=True)
            await nomic.set_permissions(user, read_messages=True)

            await nomic.send(
                delete_after=config.delay_embed,
                content=text.fill("voice", "welcome", nickname=user),
            )

        elif after is None:
            await before.set_permissions(user, overwrite=None)
            await nomic.set_permissions(user, overwrite=None)

        else:
            await before.set_permissions(user, overwrite=None)
            await after.set_permissions(user, view_channel=True)

        await self.voiceCleanup()

    async def setVoiceName(self, channel: discord.VoiceChannel):
        """Set voice channel name"""
        if len(channel.members) == 0:
            await channel.edit(name="Empty")
            return

        adjs = config.get("voice cog", "adjectives")
        nouns = config.get("voice cog", "nouns")
        name = "{} {}".format(random.choice(adjs), random.choice(nouns))
        await channel.edit(name=name)

    async def voiceCleanup(self):
        """Clear nomic, rename channels"""
        voices = self.getGuild().get_channel(config.channel_voices)
        nomic = self.getGuild().get_channel(config.channel_nomic)

        empty = None
        # Rename populated 'Empty' channels. Get last empty channel
        for v in voices.voice_channels:
            if len(v.members) == 0:
                empty = v
            elif len(v.members) > 0 and v.name == "Empty":
                await self.setVoiceName(v)

        # Remove all previous 'Empty' channels
        for v in voices.voice_channels:
            if len(v.members) == 0 and v is not empty:
                try:
                    await v.delete()
                except discord.NotFound:
                    pass

        # Move 'Empty' to end
        if empty:
            await empty.edit(name="Empty", position=len(voices.channels))
            if empty.id in self.locked:
                self.locked.remove(empty.id)
        else:
            v = await self.getGuild().create_voice_channel(name="Empty", category=voices)
            await v.set_permissions(self.getVerifyRole(), view_channel=True)

        # Clear nomic if no one is left
        if len(voices.voice_channels) == 1:
            await nomic.purge()
            self.locked = []


def setup(bot):
    bot.add_cog(Voice(bot))
