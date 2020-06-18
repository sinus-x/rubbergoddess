import hjson
import os
import random
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

        self.supported_formats = ("jpg", "jpeg", "png", "webm", "mp4", "gif")

        self.path = os.getcwd() + "/data/actress/"
        try:
            self.reactions = hjson.load(open(self.path + "reactions.hjson"))
        except:
            self.reactions = {}
        self.usage = {}

    ##
    ## Commands
    ##
    @commands.is_owner()
    @commands.group(name="send")
    async def send(self, ctx):
        """Send message to given channel"""
        await utils.send_help(ctx)

    @send.command(name="text")
    async def send_text(self, ctx, channel: discord.TextChannel, content):
        """Send a text to text channel

        channel: Target text channel
        content: Text
        """
        message = await channel.send(text)
        await self.event.sudo(
            ctx.author,
            ctx.channel,
            f"Text sent to {channel.mention if hasattr(channel, 'mention') else type(channel).__name__}:\n"
            f"> _{content}_\n> <{message.jump_url}>",
        )
        await self.output.info(ctx, "Message sent.")

    @send.command(name="image")
    async def send_image(self, ctx, channel: discord.TextChannel, filename):
        """Send an image as a bot

        channel: Target text channel
        filename: A filename
        """
        now = time.monotonic()
        try:
            async with ctx.typing():
                message = await channel.send(file=discord.File(self.path + filename))
                delta = time.monotonic() - now
                await self.output.info(ctx, f"Sent in {delta:.1f} seconds.")
                mention = channel.mention if hasattr(channel, "mention") else type(channel).__name__
                await self.event.sudo(
                    ctx.author,
                    ctx.channel,
                    f"Media file sent to {mention}:\n" f"> _{filename}_\n> <{message.jump_url}>",
                )
        except Exception as e:
            await self.output.error(ctx, "Could not send media file", e)

    @commands.check(check.is_mod)
    @commands.group(name="react", aliases=["reaction", "reactions"])
    async def react(self, ctx):
        await utils.send_help(ctx)

    @react.command(name="list")
    async def react_list(self, ctx):
        """List current reactions"""
        try:
            name = next(iter(self.reactions))
            reaction = self.reactions[name]
            embed = self.embed(ctx=ctx, page=(1, len(self.reactions)))
        except StopIteration:
            reaction = None
            embed = self.embed(ctx=ctx)

        if reaction is not None:
            embed = self.fill_reaction_embed(embed, name, reaction)

        message = await ctx.send(embed=embed)

        if len(self.reactions) > 1:
            await message.add_reaction("◀")
            await message.add_reaction("▶")

    @react.command(name="usage", aliases=["stat", "stats"])
    async def react_usage(self, ctx):
        """See reactions usage since start"""
        items = {
            k: v for k, v in sorted(self.usage.items(), key=lambda item: item[1], reverse=True)
        }

        embed = self.embed(ctx=ctx)
        content = []
        total = 0
        template = "`{count:>2}` … **{reaction}**"
        for reaction, count in items.items():
            content.append(template.format(count=count, reaction=reaction))
            total += count
        if len(content) == 0:
            content.append("Nothing yet.")

        embed.add_field(name=f"{total} in total", value="\n".join(content))
        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)

    @react.command(name="add")
    async def react_add(self, ctx, name: str = None, *, parameters=None):
        """Add new reaction

        ```
        ?react add <reaction name>
        type <image | text>
        match <full | start | end | any>
        sensitive <true | false>
        triggers "a b c" "d e" f
        responses "abc def"

        users 0 1 2
        channels 0 1 2
        counter 10
        ```
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
        """Edit reaction

        ```
        ?react edit <reaction name>
        type <image | text>
        match <full | start | end | any>
        sensitive <true | false>
        triggers "a b c" "d e" f
        responses "abc def"

        users 0 1 2
        channels 0 1 2
        counter 10
        ```
        """
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
        elif name not in self.reactions.keys():
            raise ReactionNotFound()

        del self.reactions[name]
        self._save_reactions()

        await self.output.info(ctx, f"Reaction **{name}** removed.")
        await self.event.sudo(ctx.author, ctx.channel, f"Reaction **{name}** removed.")

    @commands.is_owner()
    @commands.group(name="image", aliases=["img", "images"])
    async def image(self, ctx):
        """Manage images available to the bot"""
        await utils.send_help(ctx)

    @image.command(name="list")
    async def image_list(self, ctx):
        """List available commands"""
        files = os.listdir(self.path)
        template = "`{size:>5} kB` … {filename}"
        content = []
        for file in files:
            if file.split(".")[-1] not in self.supported_formats:
                continue
            size = int(os.path.getsize(self.path + file) / 1024)
            content.append(template.format(size=size, filename=file))
        if len(content) == 0:
            content.append("No media files found")

        embed = self.embed(ctx=ctx)
        embed.add_field(name="\u200b", value="\n".join(content))
        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)

    @image.command(name="download", aliases=["dl"])
    async def image_download(self, ctx, url: str, filename: str):
        """Download new image

        url: URL of the image
        filename: Target filename
        """
        if filename.split(".")[-1] not in self.supported_formats:
            return self.output.error(ctx, "Unsupported extension")
        if "/" in filename or "\\" in filename or ".." in filename:
            return self.output.error(ctx, "Invalid characters")

        with open(self.path + filename, "wb") as f:
            response = get(url)
            f.write(response.content)

        await self.output.info(ctx, "Image successfully downloaded.")

        await utils.delete(ctx)

    @image.command(name="remove", aliases=["delete", "rm", "del"])
    async def image_remove(self, ctx, filename: str):
        """Remove image

        filename: An image filename
        """
        if "/" in filename or "\\" in filename or ".." in filename:
            return self.output.error(ctx, "Invalid characters")

        os.remove(self.path + filename)
        await self.output.info("File deleted")

        await utils.delete(ctx)

    @image.command(name="show")
    async def image_show(self, ctx, filename: str):
        """Show an image

        filename: An image filename
        """
        await self.send_image(ctx, ctx.channel, filename)

        await utils.delete(ctx)

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for name, reaction in self.reactions.items():
            # test
            if not self._reaction_matches(message, reaction):
                continue

            # send
            response = random.choice(reaction["responses"])
            if reaction["type"] == "text":
                await message.channel.send(response.replace("{mention}", message.author.mention))
            elif reaction["type"] == "image":
                await message.channel.send(file=discord.File(self.path + response))

            # log
            if name in self.usage:
                self.usage[name] += 1
            else:
                self.usage[name] = 1

            # counter
            if "counter" in reaction:
                if reaction["counter"] > 1:
                    self.reactions[name]["counter"] -= 1
                else:
                    # last usage, delete from config
                    del self.reactions[name]
                    await self.console.info("Reaction removed: {name}")
                self._save_reactions()

            break

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # do we care?
        if user.bot:
            return

        if hasattr(reaction, "emoji"):
            if str(reaction.emoji) == "◀":
                page_delta = -1
            elif str(reaction.emoji) == "▶":
                page_delta = 1
            else:
                # invalid reaction
                return await self._remove_reaction(reaction, user)
        else:
            # invalid reaction
            return await self._remove_reaction(reaction, user)

        if len(reaction.message.embeds) != 1:
            return
        embed = reaction.message.embeds[0]
        if not embed.title.endswith("react list"):
            return await self._remove_reaction(reaction, user)
        if embed.footer == discord.Embed.Empty or " | " not in embed.footer.text:
            return await self._remove_reaction(reaction, user)

        # get page
        footer_text = embed.footer.text
        pages = footer_text.split(" | ")[-1]
        page_current = int(pages.split("/")[0]) - 1

        page = (page_current + page_delta) % len(self.reactions)
        footer_text = footer_text.replace(pages, f"{page+1}/{len(self.reactions)}")

        # update embed
        bot_reaction_name = list(self.reactions.keys())[page]
        bot_reaction = self.reactions[bot_reaction_name]

        embed = self.fill_reaction_embed(embed, bot_reaction_name, bot_reaction)
        embed.set_footer(text=footer_text, icon_url=embed.footer.icon_url)
        await reaction.message.edit(embed=embed)

        await self._remove_reaction(reaction, user)

    ##
    ## Helper functions
    ##
    def _save_reactions(self):
        with open(self.path + "reactions.hjson", "w", encoding="utf-8") as f:
            hjson.dump(self.reactions, f, ensure_ascii=False, indent="\t")

    async def _remove_reaction(self, reaction, user):
        try:
            await reaction.remove(user)
        except:
            pass

    def _reaction_matches(self, message, reaction) -> bool:
        # normalise
        if reaction["sensitive"]:
            text = message.content
            triggers = reaction["triggers"]
        else:
            text = message.content.lower()
            triggers = [x.lower() for x in reaction["triggers"]]

        # check the type
        if reaction["match"] == "full" and text not in triggers:
            return False
        if reaction["match"] == "any":
            for trigger in triggers:
                if trigger in text:
                    break
            else:
                return False
        if reaction["match"] == "start":
            for trigger in triggers:
                if text.startswith(trigger):
                    break
            else:
                return False
        if reaction["match"] == "end":
            for trigger in triggers:
                if text.endswith(trigger):
                    break
            else:
                return False

        # conditions
        if "users" in reaction and message.author.id not in reaction["users"]:
            return False
        if "channels" in reaction and message.channel.id not in reaction["channels"]:
            return False

        return True

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

            if key not in (
                "type",
                "match",
                "sensitive",
                "triggers",
                "responses",
                "users",
                "channels",
                "counter",
            ):
                raise InvalidReactionKey(key=key)

            # check
            invalid = False
            # fmt: off
            if key == "type" and value not in ("text", "image") \
            or key == "match" and value not in ("full", "start", "end", "any") \
            or key == "sensitive" and value not in ("true", "false") \
            or key == "triggers" and len(value) < 1 \
            or key == "responses" and len(value) < 1:
                invalid = True

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

    def fill_reaction_embed(self, embed: discord.Embed, name: str, reaction: dict) -> discord.Embed:
        # reset any previous
        embed.clear_fields()

        embed.add_field(name="name", value=f"**{name}**")
        for key in ("triggers", "responses"):
            value = "\n".join(reaction[key])
            embed.add_field(name=key, value=value, inline=False)
        for key in ("type", "match", "sensitive"):
            embed.add_field(name=key, value=reaction[key])
        if "users" in reaction.keys() and reaction["users"] is not None:
            users = [self.bot.get_user(x) for x in reaction["users"]]
            value = "\n".join(
                f"`{user.id}` {user.name if hasattr(user, 'name') else '_unknown_'}"
                for user in users
            )
            embed.add_field(name="users", value=value, inline=False)
        if "channels" in reaction.keys() and reaction["channels"] is not None:
            channels = [self.bot.get_channel(x) for x in reaction["channels"]]
            value = "\n".join(f"`{channel.id}` {channel.mention}" for channel in channels)
            embed.add_field(name="channels", value=value, inline=False)
        if "counter" in reaction.keys() and reaction["counter"] is not None:
            embed.add_field(name="countdown", value=str(reaction["counter"]))

        return embed

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
        if isinstance(error, InvalidReactionKey):
            await self.output.error(ctx, text.fill(
                "actress", "InvalidReactionKey", key=error.key))
        elif isinstance(error, ReactionParsingException):
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


class InvalidReactionKey(ReactionException):
    def __init__(self, key: str):
        super().__init__()
        self.key = key


class ReactionParsingException(ReactionException):
    def __init__(self, key: str, value: str):
        super().__init__()
        self.key = key
        self.value = value
