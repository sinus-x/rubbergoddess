import traceback
import smtplib

import sqlalchemy

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import rubbercog, utils
from core.config import config
from repository import acl_repo


class Errors(rubbercog.Rubbercog):
    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("errors")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):  # noqa: C901
        """Handle errors"""
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        throw_error = await self._send_exception_message(ctx, error)
        if not throw_error:
            return

        # display error message
        await self.output.error(ctx, "", error)
        output = self._format_output(ctx, error)
        print(output)

        # send traceback to dedicated channel
        channel_stdout = self.bot.get_channel(config.get("channels", "stdout"))
        output = list(output[0 + i : 1960 + i] for i in range(0, len(output), 1960))
        sent = []
        for message in output:
            m = await channel_stdout.send("```\n{}```".format(message))
            sent.append(m)

        # send notification to botdev
        await self._send_notification(ctx, output, error, sent[0].jump_url)

    ##
    ## Logic
    ##

    async def _send_exception_message(self, ctx: commands.Context, error: Exception) -> bool:
        """Return True if error should be thrown"""

        # fmt: off
        if isinstance(error, acl_repo.ACLException):
            await self.output.error(ctx, self.text.get("acl", type(error).__name__, error=str(error)))
            return False

        # cog exceptions are handled in their cogs
        if isinstance(error, rubbercog.RubbercogException):
            if type(error) is not rubbercog.RubbercogException:
                return False
            await self.output.error(ctx, self.text.get("RubbercogException"), error)
            return False

        if type(error) == commands.CommandNotFound:
            return

        # Exceptions with parameters
        if type(error) == commands.MissingRequiredArgument:
            await self.output.warning(ctx, self.text.get("MissingRequiredArgument", param=error.param.name))
            return False
        if type(error) == commands.CommandOnCooldown:
            time = utils.seconds2str(error.retry_after)
            await self.output.warning(ctx, self.text.get("CommandOnCooldown", time=time))
            return False
        if type(error) == commands.MaxConcurrencyReached:
            await self.output.warning(ctx, self.text.get("MaxConcurrencyReached", num=error.number, per=error.per.name))
            return False
        if type(error) == commands.MissingRole:
            # TODO Is !r OK, or should we use error.missing_role.name?
            role = f"`{error.missing_role!r}`"
            await self.output.warning(ctx, self.text.get("MissingRole", role=role))
            return False
        if type(error) == commands.BotMissingRole:
            role = f"`{error.missing_role!r}`"
            await self.output.error(ctx, self.text.get("BotMissingRole", role=role))
            return False
        if type(error) == commands.MissingAnyRole:
            roles = ", ".join(f"`{r!r}`" for r in error.missing_roles)
            await self.output.warning(ctx, self.text.get("MissingAnyRole", roles=roles))
            return False
        if type(error) == commands.BotMissingAnyRole:
            roles = ", ".join(f"`{r!r}`" for r in error.missing_roles)
            await self.output.error(ctx, self.text.get("BotMissingAnyRole", roles=roles))
            return False
        if type(error) == commands.MissingPermissions:
            perms = ", ".join(f"`{p}`" for p in error.missing_perms)
            await self.output.warning(ctx, self.text.get("MissingPermissions", perms=perms))
            return False
        if type(error) == commands.BotMissingPermissions:
            perms = ", ".join(f"`{p}`" for p in error.missing_perms)
            await self.output.error(ctx, self.text.get("BotMissingPermissions", perms=perms))
            return False
        if type(error) == commands.BadUnionArgument:
            await self.output.warning(ctx, self.text.get("BadUnionArgument", param=error.param.name))
            return False
        if type(error) == commands.BadBoolArgument:
            await self.output.warning(ctx, self.text.get("BadBoolArgument", arg=error.argument))
            return False

        # All cog-related errors
        if isinstance(error, smtplib.SMTPException):
            await self.stdout.error(ctx, "Could not send e-mail", error)
            await ctx.send(self.text.get("SMTPException", name=type(error).__name__))
            return False

        if type(error) == commands.ExtensionFailed:
            await self.output.error(
                ctx,
                self.text.get(
                    type(error).__name__,
                    extension=f"{error.name!r}",
                    error_name=error.original.__class__.__name__,
                    error=str(error.original),
                )
            )
            return False
        if isinstance(error, commands.ExtensionError):
            await self.output.critical(ctx, self.text.get(type(error).__name__, extension=f"{error.name!r}"))
            return False

        # The rest of client exceptions
        if isinstance(error, commands.CommandError) or isinstance(error, discord.ClientException):
            await self.output.warning(ctx, self.text.get(type(error).__name__))
            return False

        # DiscordException, non-critical errors
        if type(error) in (
            discord.errors.NoMoreItems,
            discord.errors.HTTPException,
            discord.errors.Forbidden,
            discord.errors.NotFound,
        ):
            await self.output.error(ctx, self.text.get(type(error).__name__))
            await self.console.error(ctx, type(error).__name__, error)
            return False

        # DiscordException, critical errors
        if type(error) in (discord.errors.DiscordException, discord.errors.GatewayNotFound):
            await self.output.error(ctx, self.text.get(type(error).__name__))

        # Database
        if isinstance(error, sqlalchemy.exc.SQLAlchemyError):
            error_name = ".".join([type(error).__module__, type(error).__name__])
            await self.output.critical(ctx, error_name)
            await self.console.critical(ctx, "Database error", error)
            await self.event.user(
                ctx,
                f"Database reported`{error_name}`. The session may be invalidated <@{config.admin_id}>",
                escape_markdown=False,
            )
            return False
        # fmt: on

        return True

    def _format_output(self, ctx: commands.Context, error) -> str:
        if isinstance(ctx.channel, discord.TextChannel):
            location = f"{ctx.guild.name}/{ctx.channel.name} ({ctx.channel.id})"
        else:
            location = type(ctx.channel).__name__

        output = "{command} by {user} in {location}\n".format(
            command=config.prefix + ctx.command.qualified_name,
            user=str(ctx.author),
            location=location,
        )

        output += "".join(traceback.format_exception(type(error), error, error.__traceback__))

        return output

    async def _send_notification(
        self, ctx: commands.Context, output: str, error: Exception, traceback_url: str
    ):
        channel = self.bot.get_channel(config.channel_botdev)
        embed = self.embed(ctx=ctx, color=discord.Color.from_rgb(255, 0, 0))

        # fmt: off
        footer = "{user} in {channel}".format(
            user=str(ctx.author),
            channel=ctx.channel.name
            if isinstance(ctx.channel, discord.TextChannel)
            else type(ctx.channel).__name__
        )
        embed.set_footer(text=footer, icon_url=ctx.author.avatar_url)

        stack = output[-1]
        if len(stack) > 255:
            stack = "…" + stack[-255:]
        embed.add_field(
            name=type(error).__name__,
            value=f"```{stack}```",
            inline=False,
        )
        embed.add_field(name="Traceback", value=traceback_url, inline=False)
        await channel.send(embed=embed)
        # fmt: on
