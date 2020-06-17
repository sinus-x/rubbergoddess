import hjson
import os
import shlex
import time
from requests import get

import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text


class Actress(rubbercog.Rubbercog):
    """Be a human"""

    def __init__(self, bot):
        super().__init__(bot)

        self.path = os.getcwd() + "/data/actress/reactions.hjson"
        try:
            self.reactions = hjson.load(open(self.path))
        except:
            self.reactions = {}
        self.usage = {}

    ##
    ## Commands
    ##

    """
    ?send text <channel> <text>
    ?send image <channel> <path>

    ?react list
    ?react usage
    ?react add <name>
    type <image|text>
    match <full|start|end|any>
    caps <ignore|match>
    triggers "t1" "t 2"
    response "string"
    users 0 1 2
    channels 0 1 2
    ?react remove <name>
    ?react edit <name>
    match <full|start|end|any>
    caps <ignore|match>
    triggers "t1" "t 2"
    response "string"

    ?image list
    ?image download <url> <filename>
    ?image show <filename>

    ?change avatar
    ?change name
    """

    @commands.check(check.is_mod)
    @commands.group(name="react", aliases=["reaction", "reactions"])
    async def react(self, ctx):
        await utils.send_help(ctx)

    @react.command(name="list")
    async def react_list(self, ctx):
        """List current reactions"""
        # TODO Implement scrolling embed
        pass

    @react.command(name="add")
    async def react_add(self, ctx, name: str = None, *, parameters=None):
        """Add new reaction

        ?react add <reaction name>
        type <image | text>
        match <full | start | end | any>
        sensitive <true | false>
        triggers "a b c" "d e" f
        responses "abc def"

        users 0 1 2
        channels 0 1 2
        counter <int>
        """
        if name is None:
            return await utils.send_help(ctx)
        elif name in self.reactions.keys():
            raise ReactionNameExists()

        reaction = await self.parse_react_message(ctx.message, strict=True)
        self.reactions[name] = reaction
        self._save_reactions()

        await self.output.info(ctx, f"Reaction **{name}** added.")
        await self.event.sudo(ctx.author, ctx.channel, f"Reaction **{name}** added.")

    @react.command(name="edit")
    async def react_edit(self, ctx, name: str = None, *, parameters=None):
        """Edit reaction"""
        if name is None:
            return await utils.send_help(ctx)
        elif name not in self.reactions.keys():
            raise ReactionNotFound()

        new_reaction = await self.parse_react_message(ctx.message, strict=False)
        reaction = self.reactions[name]

        for key, value in reaction.items():
            if key in new_reaction.keys():
                reaction[key] = new_reaction[key]

        self.reactions[name] = reaction
        self._save_reactions()

        await self.output.info(ctx, f"Reaction **{name}** updated.")
        await self.event.sudo(ctx.author, ctx.channel, f"Reaction **{name}** updated.")

    @react.command(name="remove")
    async def react_remove(self, ctx, name: str = None):
        """Remove reaction"""
        if name is None:
            return await utils.send_help(ctx)
        elif name not in self.reaction.keys():
            raise ReactionNotFound()

        del self.reactions[name]
        self._save_reactions()

        await self.output.info(ctx, f"Reaction **{name}** removed.")
        await self.event.sudo(ctx.author, ctx.channel, f"Reaction **{name}** removed.")

    ##
    ## Listeners
    ##

    ##
    ## Helper functions
    ##
    def _save_reactions(self):
        with open(self.path, "w", encoding="utf-8") as f:
            hjson.dump(self.reactions, f, ensure_ascii=False, indent="\t")

    ##
    ## Logic
    ##
    async def parse_react_message(self, message: discord.Message, strict: bool) -> dict:
        content = message.content.replace("`", "").split("\n")[1:]
        result = {}

        # fill values
        for line in content:
            line = line.split(" ", 1)
            key = line[0]
            value = line[1]

            # check
            invalid = False
            # fmt: off
            if key == "type" and value not in ("text", "image") \
            or key == "match" and value not in ("full", "start", "end", "any") \
            or key == "sensitive" and value not in ("true", "false") \
            or key == "triggers" and len(value) < 1 \
            or key == "responses" and len(value) < 1:
                invalid = True
            elif key not in ("users", "channels", "counter"):
                # unsupported key
                continue

            # fmt: on
            if invalid:
                raise ReactionParsingException(key, value)

            # parse
            if key == "sensitive":
                value = value == "true"
            elif key in ("triggers", "responses"):
                # convert to list
                value = shlex.split(value)
            elif key in ("users", "channels"):
                # convert to list of ints
                try:
                    value = [int(x) for x in shlex.split(value)]
                except:
                    raise ReactionParsingException(key, value)
            elif key == "counter":
                try:
                    value = int(value)
                except:
                    raise ReactionParsingException(key, value)

            result[key] = value

        if strict:
            # check if all required values are present
            for key in ("type", "match", "triggers", "response"):
                if key is None:
                    raise discord.MissingRequiredArgument(param=key)

        return result

    ##
    ## Error catching
    ##
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # try to get original error
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        # non-rubbergoddess exceptions are handled globally
        if not isinstance(error, rubbercog.RubbercogException):
            return

        # fmt: off
        # exceptions with parameters
        if isinstance(error, ReactionParsingException):
            await self.output.error(ctx, text.fill(
                "actress", "ReactionParsingException", key=error.key, value=error.value))
        # exceptions without parameters
        elif isinstance(error, ActressException):
            await self.output.error(ctx, text.get("actress", type(error).__name__))
        # fmt: on


def setup(bot):
    bot.add_cog(Actress(bot))


class ActressException(rubbercog.RubbercogException):
    pass


class ReactionException(ActressException):
    pass


class ReactionNameExists(ReactionException):
    pass


class ReactionNotFound(ReactionException):
    pass


class ReactionParsingException(ReactionException):
    def __init__(self, key: str, value: str):
        super().__init__()
        self.key = key
        self.value = value
