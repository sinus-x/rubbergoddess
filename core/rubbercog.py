import datetime
import re
import traceback

import discord
from discord.ext import commands

from core import output
from core.config import config
from core.text import text


class Rubbercog(commands.Cog):
    """Main cog class"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.slave = None
        self.guild = None
        self.role_mod = None
        self.role_verify = None
        self.roles_elevated = None
        self.roles_native = None

        self.output = output.Output(self.bot)
        self.console = output.Console(self.bot)
        self.event = output.Event(self.bot)

    ##
    ## OBJECT GETTERS
    ##
    def getGuild(self):
        if self.guild is None:
            self.guild = self.bot.get_guild(config.guild_id)
        return self.guild

    def getSlave(self):
        if self.slave is None:
            self.slave = self.bot.get_guild(config.slave_id)
        return self.slave

    def getModRole(self):
        if self.role_mod is None:
            self.role_mod = self.getGuild().get_role(config.role_mod)
        return self.role_mod

    def getVerifyRole(self):
        if self.role_verify is None:
            self.role_verify = self.getGuild().get_role(config.role_verify)
        return self.role_verify

    def getElevatedRoles(self):
        if self.roles_elevated is None:
            self.roles_elevated = [self.getGuild().get_role(x) for x in config.roles_elevated]
        return self.roles_elevated

    def getNativeRoles(self):
        if self.roles_native is None:
            self.roles_native = [self.getGuild().get_role(x) for x in config.roles_native]
        return self.roles_native

    ##
    ## Helper functions
    ##
    def _getEmbedTitle(self, ctx: commands.Context):
        """Helper function assembling title for embeds"""
        if ctx.command is None:
            return "(no command)"

        path = (
            " ".join((p.name) for p in ctx.command.parents[::-1]) + " "
            if ctx.command.parents
            else ""
        )
        return config.prefix + path + ctx.command.name

    def _getEmbed(self, ctx: commands.Context, color: int = None, pin=False):
        """Helper function for creating embeds

        color: embed color
        pin: whether to pin the embed or let it be deleted
        """
        if color not in config.colors:
            color = config.color
        if pin is not None and pin:
            title = "📌 " + self._getEmbedTitle(ctx)
        else:
            title = self._getEmbedTitle(ctx)
        description = "**{}**".format(ctx.command.cog_name) if ctx.command else ""

        embed = discord.Embed(title=title, description=description, color=color)
        if ctx.author is not None:
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        return embed

    def _getCommandSignature(self, ctx: commands.Context):
        """Return a 'cog:command_name' string"""
        if not ctx.command:
            return "UNKNOWN"
        name = ctx.command.qualified_name.replace(" ", "_")
        if not ctx.command.cog:
            return name
        else:
            return "{}:{}".format(ctx.command.cog.qualified_name.lower(), name)

    ##
    ## Utils
    ##
    async def log(self, ctx, action: str, quote: bool = True, msg=None):
        """Log event"""
        channel = self.getGuild().get_channel(config.channel_guildlog)
        author = self.getGuild().get_member(ctx.author.id)
        if author.top_role.id in config.roles_elevated:
            user = "{r} **{u}**".format(u=author.name, r=author.top_role.name.lower())
        else:
            user = ctx.author.mention
        if isinstance(ctx.channel, discord.DMChannel):
            message = "**{}** by {} in DM".format(action, user)
        else:
            message = "**{}** by {} in {}".format(action, user, ctx.channel.mention)

        if ctx.guild and ctx.guild.id != config.guild_id:
            message += " (**{}**/{})".format(ctx.guild.name, ctx.guild.id)

        if msg is not None or quote is not None:
            message += ": "
        if msg is not None:
            if type(msg).__name__ == "str":
                message += msg
            else:
                message += type(msg).__name__
        if quote:
            message += "\n> _{}_".format(ctx.message.content)
        await channel.send(message)

    async def roomCheck(self, ctx: commands.Context):
        """Send an message to prevent bot spamming"""
        if isinstance(ctx.channel, discord.DMChannel):
            return
        botspam = self.getGuild().get_channel(config.channel_botspam)
        if ctx.channel.id not in config.bot_allowed:
            await ctx.send(
                text.fill("server", "botroom redirect", user=ctx.author, channel=botspam)
            )

    # TODO Rename to deleteMessage()
    async def deleteCommand(self, message, *, delay: int = 0):
        """Try to delete the context message.

        now: Do not wait for message delay
        """
        try:
            if not isinstance(message, discord.Message):
                message = message.message
            await message.delete(delay=delay)
        except discord.HTTPException:
            pass

    def parseArg(self, arg: str = None):
        """Return true if supported argument is matched"""
        # TODO Do this the proper way
        args = ["pin", "force"]
        return True if arg in args else False

    def getTimestamp(self):
        """Get yyyy-mm-dd HH:MM:SS string"""
        return datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    def sanitise(self, string: str, *, limit: int = 500):
        """Return cleaned-up string ready for output"""
        return discord.utils.escape_markdown(string).replace("@", "")[:limit]

    ##
    ## Embeds
    ##
    # TODO This code is deprecated. We should just raise the exception, so it is caught by Errors cog
    async def throwError(self, ctx: commands.Context, err, delete: bool = False, pin: bool = False):
        """Show an embed and log the error"""
        # Get error information
        if isinstance(err, Exception):
            err = getattr(err, "original", err)
            err_type = type(err).__name__
            err_trace = "".join(traceback.format_exception(type(err), err, err.__traceback__))
        else:
            err_type = "RubbergoddessException"
            err_trace = "No traceback\n**{}**".format(err)
        err_title = "{}: {}".format(ctx.author, ctx.message.content)

        # Do the debug
        if config.debug >= 1:
            print("ERROR OCCURED: " + err_title)  # noqa: T001
            print("ERROR TRACE: " + err_trace)  # noqa: T001
        if config.debug >= 2:
            await self.sendLong(ctx, "[debug=2] Error: " + err_title + "\n" + err_trace, code=True)
        # Clean the input
        content = ctx.message.content
        content = content if len(content) < 600 else content[:600]
        delete = False if pin else delete

        if len(err_trace) > 600:
            err_trace = err_trace[-600:]
        # Construct the error embed
        embed = self._getEmbed(ctx, color=config.color_error, pin=pin)
        embed.add_field(name=err_type, value=f"```{err_trace}```", inline=False)
        embed.add_field(name="Command", value=content, inline=False)
        if delete:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        else:
            await ctx.send(embed=embed)
        await self.deleteCommand(ctx, delay=0)
        await self.log(ctx, self._getCommandSignature(ctx), quote=True, msg=err_type)

    # TODO This code is deprecated. Use self.output.info() instead
    async def throwNotification(self, ctx: commands.Context, msg: str, pin: bool = False):
        """Show an embed with a message."""
        msg = str(msg)
        # Do the debug
        title = "{}: {}".format(ctx.author, ctx.message.content)
        if config.debug >= 1:
            print("NOTIFICATION: " + title)  # noqa: T001
            print("NOTIFY TRACE: " + msg)  # noqa: T001
        if config.debug >= 2:
            await self.sendLong(ctx, "[debug=2] Notification: " + title + "\n" + msg, code=True)

        # Clean the input
        content = ctx.message.content
        if len(str(content)) > 512:
            content = str(content)[:512]
        content = content if len(content) < 512 else content[:512]

        # Construct the notification embed
        embed = self._getEmbed(ctx, color=config.color_notify, pin=pin)
        embed.add_field(name="Notification", value=msg, inline=False)
        embed.add_field(name="Command", value=content, inline=False)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, delay=0)

    # TODO This code is deprecated. Use ctx.send_help() instead
    async def throwDescription(self, ctx: commands.Context, pin: bool = False):
        """Show an embed with full docstring content."""
        embed = self._getEmbed(ctx)
        embed.add_field(name="About", value=ctx.command.short_doc)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, delay=0)

    # TODO This code is deprecated. Use ctx.send_help() instead
    async def throwHelp(self, ctx: commands.Context, pin: bool = False):
        """Show help for command groups"""
        embed = self._getEmbed(ctx)
        embed.add_field(name="Help", value=self.__formatHelp(ctx.command.help))

        if isinstance(ctx.command, commands.Group) and ctx.command.commands:
            embed.add_field(name="-" * 60, value="**SUBCOMMANDS**:", inline=False)
            for opt in ctx.command.commands:
                embed.add_field(name=opt.name, value=opt.short_doc, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, delay=0)

    # TODO Move helper functions here
    ##
    ## HELPER FUNCTIONS
    ##
    async def sendLong(self, ctx: commands.Context, message: str, code: bool = False):
        """Send messages that may exceed the 2000-char limit

        message: The text to be sent
        code: Whether to format the output as a code
        """
        message = list(message[0 + i : 1960 + i] for i in range(0, len(message), 1960))
        for m in message:
            if code:
                await ctx.send("```\n{}```".format(m))
            else:
                await ctx.send(m)

    def __formatHelp(self, text: str):
        if not text:
            return "_(No help available)_"
        text = text.split("\n")
        text[0] = f"**{text[0]}**"
        for i in range(2, len(text)):
            match = re.findall(r"([a-zA-Z]+)(:)", text[i])[0][0]
            text[i] = text[i].replace(match, f"**{match}**", 1)
        return "\n".join(text)
