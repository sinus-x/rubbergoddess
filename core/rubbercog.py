import datetime
from typing import Union

import discord
from discord.ext import commands

from core import output
from core.config import config


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
    ## DEPRECATED Utils
    ##
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

    ##
    ## Utils
    ##

    def getTimestamp(self):
        """Get yyyy-mm-dd HH:MM:SS string"""
        return datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    def sanitise(self, string: str, *, limit: int = 500, markdown: bool = False):
        """Return cleaned-up string ready for output"""
        if not markdown:
            string = discord.utils.escape_markdown(string)
        return string.replace("@", "@\u200b")[:limit]

    def embed(
        self,
        *,
        ctx: commands.Context = None,
        message: discord.Message = None,
        author: discord.User = None,
        title: str = None,
        description: str = None,
        color: int = None,
        page: tuple = None,
        footer: str = None,
        url: Union[str, discord.Embed.Empty] = discord.Embed.Empty,
    ) -> discord.Embed:
        """Create embed

        page: tuple in (current, total) format
        """
        # author
        if hasattr(ctx, "author"):
            author = ctx.author
            footer_image = author.avatar_url
        elif hasattr(message, "author"):
            author = message.author
            footer_image = author.avatar_url
        else:
            author = None
            footer_image = discord.Embed.Empty

        # title
        if title is not None:
            pass
        elif hasattr(ctx, "command") and hasattr(ctx.command, "qualified_name"):
            title = config.prefix + ctx.command.qualified_name
        else:
            title = "Rubbergoddess"

        # description
        if description is not None:
            pass
        elif hasattr(ctx, "cog_name"):
            description = f"**{ctx.cog_name}**"
        else:
            description = ""

        # color
        if color is None:
            color = config.color

        # footer text
        footer_content = []
        if author is not None:
            footer_content.append(str(author))
        if footer is not None:
            footer_content.append(footer)
        if page is not None:
            footer_content.append(f"{page[0]}/{page[1]}")
        footer_text = " | ".join(footer_content)

        # create embed
        embed = discord.Embed(title=title, description=description, color=color, url=url)
        if footer_image is not discord.Embed.Empty or len(footer_text) > 0:
            embed.set_footer(icon_url=footer_image, text=footer_text)

        # add footer timestamp
        embed.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

        # done
        return embed


##
## Exceptions
##


class RubbercogException(Exception):
    def __init__(self, message: str = None):
        self.message = message
