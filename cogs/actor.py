import discord
from discord.ext import commands

from core import rubbercog, check
from config import config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

class Actor(rubbercog.Rubbercog):
    """Be a human"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.group(name="send")
    @commands.check(check.is_mod)
    async def send(self, ctx: commands.Context):
        """Send post to a channel"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            await self.deleteCommand(ctx)
            return

    @send.command(name="text")
    async def send_text(self, ctx: commands.Context, channel: discord.TextChannel = None, *args):
        """Send a text message as a bot

        channel: Target text channel
        message: Text
        """
        text = ' '.join(args) if args else None
        if channel is None or text is None:
            await self.throwHelp(ctx)
            return

        await channel.send(text)
        await self.deleteCommand(ctx)

    @send.command(name="image")
    async def send_image(self, ctx: commands.Context, channel: discord.TextChannel = None, url):
        """Send an image as a bot

        channel: Target text channel
        message: Path to an image or a url
        """
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)


    @commands.group(name="actor")
    @commands.check(check.is_bot_owner)
    async def actor(self, ctx: commands.Context):
        """Send post to a text channel"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            await self.deleteCommand(ctx)
            return

    @actor.command(name="list")
    async def actor_list(self, ctx: commands.Context):
        """See current reactions"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)

    @actor.group(name="add")
    async def actor_add(self, ctx: commands.Context):
        """Add reaction"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            await self.deleteCommand(ctx)
            return

    @actor_add.command(name="text")
    async def actor_add_text(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)

    @actor_add.command(name="image")
    async def actor_add_image(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)

    @actor.group(name="remove")
    async def actor_remove(self, ctx: commands.Context):
        """Add reaction"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            await self.deleteCommand(ctx)
            return

    @actor_add.command(name="text")
    async def actor_remove_text(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)

    @actor_add.command(name="image")
    async def actor_remove_image(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)


    @commands.check(check.is_bot_owner)
    @commands.group(name="bot")
    async def self(self, ctx: commands.Context, type: str, *args):
        """Change the bot"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            await self.deleteCommand(ctx)
            return

    @bot.command(name="avatar")
    async def self_avatar(self, ctx: commands.Context, path: str):
        """Change bot's avatar"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)

    @bot.command(name="name")
    async def self_name(self, ctx: commands.Context, *args):
        """Change bot's name

        name: New name
        """
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)

    @bot.command(name="activity")
    async def self_activity(self, ctx: commands.Context, type: str, name: str):
        """Change bot's activity

        type: streaming, playing, listening
        name: The activity name
        """
        await self.throwNotification(ctx, messages.err_not_implemented)
        await self.deleteCommand(ctx)



def setup(bot):
    bot.add_cog(Actor(bot))
