import datetime
import traceback

from discord.ext import commands

from core import rubbercog
from core.text import text
from core.config import config


class Errors(rubbercog.Rubbercog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):  # noqa: C901
        """Handle errors"""
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        # TODO Implement all exceptions
        # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exceptions

        # user interaction
        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_perms)
            await self.output.error(
                ctx, text.fill("error", "no user permission", permissions=perms)
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_perms)
            await self.output.error(ctx, text.fill("error", "no bot permission", permissions=perms))
            await self.console.error(ctx, "I'm missing permissions: " + perms)
            return

        if isinstance(error, commands.CommandOnCooldown):
            time = datetime.timedelta(error.retry_after)
            await self.output.error(ctx, text.fill("error", "cooldown", time=time))
            return

        if isinstance(error, commands.MaxConcurrencyReached):
            await self.output.error(
                ctx,
                text.fill("error", "concurrency", number=error.number, bucket_type=error.per.name),
            )

        if isinstance(error, commands.NSFWChannelRequired):
            await self.output.error("error", "nsfw required")
            return

        if isinstance(error, commands.CheckFailure):
            # Should we send _which_ checks failed?
            await self.output.error(ctx, text.get("error", "no requirement"))
            return

        if isinstance(error, commands.BadArgument):
            await self.output.error(ctx, text.get("error", "bad argument"))
            return

        if isinstance(error, commands.ExpectedClosingQuoteError):
            await self.output.error(ctx, text.get("error", "bad argument"))
            return

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await self.output.error(
                ctx, text.fill("error", "missing argument", argument=error.param.name)
            )
            return

        if isinstance(error, commands.ArgumentParsingError):
            await self.output.error(ctx, text.get("error", "argument parsing"))
            return

        elif isinstance(error, commands.CommandError):
            await self.output.error(ctx, text.get("error" "command"), error)
            return

        # cog loading
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            return await self.output.error(ctx, text.get("error", "extension loaded"))
        elif isinstance(error, commands.ExtensionNotLoaded):
            return await self.output.error(ctx, text.get("error", "extension not loaded"))
        elif isinstance(error, commands.ExtensionFailed):
            return await self.output.error(ctx, text.get("error", "extenson failed"))
        elif isinstance(error, commands.ExtensionNotFound):
            return await self.output.error(ctx, text.get("error", "extension not found"))
        elif isinstance(error, commands.ExtensionError):
            return await self.output.error(ctx, text.get("error", "extension"), error)
        # fmt: on

        # display error message
        await self.throwError(ctx, error)
        await self.log(ctx, "on_command_error", quote=True, msg=error)

        output = "Ignoring exception in command {}: \n\n".format(ctx.command)
        output += "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # print traceback to stdout
        print(output)

        # send traceback to dedicated channel
        channel = self.bot.get_channel(config.channel_botdev)
        output = list(output[0 + i : 1960 + i] for i in range(0, len(output), 1960))
        if channel is not None:
            for message in output:
                await channel.send("```\n{}```".format(message))


def setup(bot):
    bot.add_cog(Errors(bot))
