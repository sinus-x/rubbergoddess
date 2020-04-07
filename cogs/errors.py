import traceback

import discord
from discord.ext import commands

from core import utils
from core.rubbercog import Rubbercog
from config.config import config
from config.emotes import Emotes as emote
from config.messages import Messages as messages

class Errors(Rubbercog):
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.Cog.listener()
    async def on_command_error (self, ctx: commands.Context, error):
        """Handle errors"""
        if hasattr(ctx.command, 'on_error') or \
           hasattr(ctx.command, 'on_command_error'):
            return
        error = getattr(error, 'original', error)

        if isinstance(error, commands.MissingPermissions):
            await self.throwNotification(ctx, messages.err_no_permission)
            return

        if isinstance(error, commands.CommandOnCooldown):
            await self.throwNotification(ctx, messages.err_cooldown)
            return

        elif isinstance(error, commands.CheckFailure):
            await self.throwNotification(ctx, messages.err_no_requirements)
            return

        elif isinstance(error, commands.BadArgument):
            await self.throwNotification(ctx, messages.err_bad_argument)
            return

        elif isinstance(error, commands.CommandNotFound):
            if not ctx.message.content[0] in config.prefixes:
                await self.throwNotification(ctx, messages.err_no_command)
            return

        elif isinstance(error, commands.ExtensionError):
            await self.throwError(ctx, messages.err_extension_err)
            return

        # display error message
        await self.throwError(ctx, ctx.message.content)

        output = 'Ignoring exception in command {}: \n\n'.format(ctx.command)
        output += ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        # print traceback to stdout
        print(output)
        # send traceback to dedicated channel
        channel = self.bot.get_channel(config.channel_botdev)
        output = list(output[0+i:1960+i] for i in range(0, len(output), 1960))
        if channel is not None:
            for message in output:
                await channel.send("```\n{}```".format(message))


def setup(bot):
    bot.add_cog(Errors(bot))
