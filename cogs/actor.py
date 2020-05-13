import discord
from discord.ext import commands

from core import check, rubbercog
from core.config import config
from core.emote import emote
from core.text import text

class Actor(rubbercog.Rubbercog):
    """Be a human"""
    def __init__(self, bot):
        super().__init__(bot)

    @commands.group(name="send")
    @commands.check(check.is_bot_owner)
    async def send(self, ctx: commands.Context):
        """Send post to a channel"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @send.command(name="text")
    async def send_text(self, ctx: commands.Context, channel: discord.TextChannel, *, text: str):
        """Send a text message as a bot

        channel: Target text channel
        message: Text
        """
        if channel is None or text is None:
            await self.deleteCommand(ctx)
            await ctx.send_help(ctx.invoked_with)
            return

        await channel.send(text)
        await self.deleteCommand(ctx)

    @send.command(name="image")
    async def send_image(self, ctx: commands.Context, channel: discord.TextChannel, url):
        """Send an image as a bot

        channel: Target text channel
        message: A path or an url to an image
        """
        await self.output.info(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)

    @commands.group(name="actor")
    @commands.check(check.is_bot_owner)
    async def actor(self, ctx: commands.Context):
        """Send post to a text channel"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @actor.command(name="list")
    async def actor_list(self, ctx: commands.Context):
        """See current reactions"""
        await self.throwNotification(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)

    @actor.group(name="add")
    async def actor_add(self, ctx: commands.Context):
        """Add reaction"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @actor_add.command(name="text")
    async def actor_add_text(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)

    @actor_add.command(name="image")
    async def actor_add_image(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)

    @actor.group(name="remove")
    async def actor_remove(self, ctx: commands.Context):
        """Add reaction"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @actor_remove.command(name="text")
    async def actor_remove_text(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)

    @actor_remove.command(name="image")
    async def actor_remove_image(self, ctx: commands.Context):
        """Add text reaction"""
        await self.throwNotification(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)


    @commands.cooldown(rate=1, per=600.0, type=commands.BucketType.default)
    @commands.check(check.is_bot_owner)
    @commands.check(check.is_in_modroom)
    @commands.group(name="change")
    async def change(self, ctx: commands.Context):
        """Change the bot"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.invoked_with)

    @change.command(name="avatar")
    async def change_avatar(self, ctx: commands.Context, path: str):
        """Change bot's avatar"""
        path = f"images/{path}"
        with open(path, 'rb') as img:
            avatar = img.read()
            await self.bot.user.edit(avatar=avatar)
            await ctx.send(content="Dobře, takhle teď budu vypadat:", file=discord.File(path))

    @change.command(name="name")
    async def change_name(self, ctx: commands.Context, *args):
        """Change bot's name

        name: New name
        """
        name = ' '.join(args)
        await self.bot.user.edit(username=name)
        await ctx.send(f"Dobře, od teď jsem **{name}**")

    @change.command(name="activity")
    async def change_activity(self, ctx: commands.Context, type: str, name: str):
        """Change bot's activity

        type: streaming, playing, listening
        name: The activity name
        """
        await self.throwNotification(ctx, text.get('error', 'not implemented'))
        await self.deleteCommand(ctx)



def setup(bot):
    bot.add_cog(Actor(bot))
