import traceback

from discord.ext import commands

from core.config import config
from core import rubbercog
from config.messages import Messages as messages


class Errors(rubbercog.Rubbercog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Handle errors"""
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        printed = False
        if config.debug == 2:
            print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
            printed = True

        # user interaction
        if isinstance(error, commands.MissingPermissions):
            await self.throwNotification(ctx, messages.err_no_permission)
            await self.log(ctx, self._getCommandSignature(ctx), quote=True, msg=error)
            return

        if isinstance(error, commands.BotMissingPermissions):
            await self.throwNotification(ctx, messages.err_no_permission_bot)
            await self.log(ctx, self._getCommandSignature(ctx), quote=True, msg=error)
            return

        if isinstance(error, commands.CommandOnCooldown):
            await self.throwNotification(ctx, messages.err_cooldown)
            return

        elif isinstance(error, commands.CheckFailure):
            await self.throwNotification(ctx, messages.err_no_requirements)
            await self.log(ctx, self._getCommandSignature(ctx), quote=True, msg=error)
            return

        elif isinstance(error, commands.BadArgument):
            await self.throwNotification(ctx, messages.err_bad_argument)
            return
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await self.throwNotification(ctx, messages.err_bad_argument)
            return

        elif isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await self.throwNotification(ctx, error)
            await self.log(ctx, "Missing argument", quote=True, msg=error)
            return

        elif isinstance(error, commands.CommandError):
            return await self.throwNotification(ctx, error)

        # cog loading
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            return await self.throwError(ctx, "The cog is already loaded")
        elif isinstance(error, commands.ExtensionNotLoaded):
            return await self.throwError(ctx, "The cog is not loaded")
        elif isinstance(error, commands.ExtensionFailed):
            return await self.throwError(ctx, "The cog failed")
        elif isinstance(error, commands.ExtensionNotFound):
            return await self.throwError(ctx, "No such cog")
        elif isinstance(error, commands.ExtensionError):
            return await self.throwError(ctx, error)
        # fmt: on

        # display error message
        await self.throwError(ctx, error)
        await self.log(ctx, "on_command_error", quote=True, msg=error)

        output = "Ignoring exception in command {}: \n\n".format(ctx.command)
        output += "".join(traceback.format_exception(type(error), error, error.__traceback__))
        # print traceback to stdout
        if not printed:
            print(output)
        # send traceback to dedicated channel
        channel = self.bot.get_channel(config.channel_botdev)
        output = list(output[0 + i : 1960 + i] for i in range(0, len(output), 1960))
        if channel is not None:
            for message in output:
                await channel.send("```\n{}```".format(message))


def setup(bot):
    bot.add_cog(Errors(bot))
