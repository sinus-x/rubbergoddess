import json
import os
import time

import discord
from discord.ext import commands
from requests import get

from core import check, rubbercog, utils
from core.config import config
from core.text import text


class Actor(rubbercog.Rubbercog):
    """Be a human"""

    def __init__(self, bot):
        super().__init__(bot)
        self.path = os.getcwd() + "/data/actor/"
        self.reactions_path = self.path + "reactions.json"
        try:
            self.reactions = json.load(open(self.reactions_path))
        except:
            self.reactions = []
        self.reactions_usage = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for name, reaction in self.reactions.items():
            text = message.content.lower()
            # fmt: off
            if reaction["match"] == "full" and reaction["trigger"] == text \
            or reaction["match"] == "any" and reaction["trigger"] in text \
            or reaction["match"] == "starts" and text.startswith(reaction["trigger"]) \
            or reaction["match"] == "ends" and text.endswith(reaction["trigger"]):
                # conditions
                if "user" in reaction and message.author.id not in reaction["user"]:
                    continue
                if "channel" in reaction and message.channel.id not in reaction["channel"]:
                    continue

                # send
                if reaction["type"] == "text":
                    await message.channel.send(reaction["response"])
                elif reaction["type"] == "image":
                    await message.channel.send(file=discord.File(self.path + reaction["response"]))

                # log
                if name in self.reactions_usage:
                    self.reactions_usage[name] += 1
                else:
                    self.reactions_usage[name] = 1
            # fmt: on

    def _save_reactions(self):
        with open(self.reactions_path, "w", encoding="utf-8") as f:
            json.dump(self.reactions, f, ensure_ascii=False, indent=4)

    def _check_match_string(self, match: str):
        """Check if match string is valid"""
        return match.upper() in ["full", "any", "starts", "ends"]

    def _check_filename_extension(self, filename: str):
        return filename.split(".")[-1] in ["jpg", "jpeg", "png", "webm", "mp4", "gif"]

    @commands.group(name="send")
    @commands.check(check.is_bot_owner)
    async def send(self, ctx):
        """Send post to a channel"""
        await utils.send_help(ctx)

    @send.command(name="text")
    async def send_text(self, ctx, channel: discord.TextChannel, *, text: str):
        """Send a text message as a bot

        channel: Target text channel
        message: Text
        """
        if channel is None or text is None:
            return await ctx.send_help(ctx.invoked_with)

        ch = self.getGuild().get_channel(config.channel_mods)
        m = await channel.send(text)
        await self.event.sudo(
            ctx.author,
            ctx.channel,
            f"Text sent to {channel.mention}:\n> _{ctx.message.content}_\n> {m.jump_url}",
        )

    @send.command(name="image")
    async def send_image(self, ctx, channel: discord.TextChannel, filename):
        """Send an image as a bot

        channel: Target text channel
        filename: A filename
        """
        await utils.send_help(ctx)

        now = time.monotonic()
        try:
            async with ctx.typing():
                m = await channel.send(file=discord.File(self.path + filename))
                delta = time.monotonic() - now
                ch = self.getGuild().get_channel(config.channel_mods)
                await self.event.sudo(
                    ctx.author,
                    ctx.channel,
                    f"Media file sent to {channel.mention} in {delta:.1f} seconds:\n"
                    f"> _{ctx.message.content}_\n> {m.jump_url}",
                )
        except Exception as e:
            await self.throwError(ctx, "Could not send media file", e)

    @commands.group(name="reactions", aliases=["reaction", "react"])
    @commands.check(check.is_mod)
    async def reactions(self, ctx):
        """Send post to a text channel"""
        await utils.send_help(ctx)

    @reactions.command(name="list")
    async def reactions_list(self, ctx):
        """See enabled reactions"""
        result = []

        for key, value in self.reactions.items():
            line = []
            # id and comment
            # fmt: off
            line.append("{match} {type} [{key}]".format(
                match=value["match"],
                type=value["type"],
                key=key,
                ) + (f" {value['comment']}" if ("comment" in value) else "")
            )

            # trigger and response
            line.append(" {trigger} -> {response}".format(
                trigger=value["trigger"],
                response=value["response"],
            ))

            # user constraints
            if "user" in value:
                users = []
                for user_id in value["user"]:
                    obj = self.bot.get_user(user_id)
                    users.append(
                        f"{user_id} ({obj.name})"
                        if hasattr(obj, "name")
                        else str(user_id)
                    )
                line.append(" " + ", ".join(users))

            # channel constraints
            if "channel" in value:
                channels = []
                for channel_id in value["channel"]:
                    obj = self.bot.get_channel(channel_id)
                    channels.append(
                        f"{channel_id} ({obj.name})"
                        if hasattr(obj, "name")
                        else str(channel_id)
                    )
                line.append(" " + ", ".join(channels))
            result.append("\n".join(line))
            # fmt: on

        if len(result) == 0:
            result = "(No reactions)"

        message = "\n".join(result)
        await ctx.send(f"```\n{message}\n```")

        await utils.delete(ctx)

    @reactions.command(name="usage", aliases=["stat", "stats", "statistics"])
    async def reactions_usage(self, ctx):
        """See reactions usage since start"""
        items = {
            k: v
            for k, v in sorted(self.reactions_usage.items(), key=lambda item: item[1], reverse=True)
        }

        embed = discord.Embed(
            title="Bot reaction", description="Trigger statistics", color=config.color,
        )

        content = []
        total = 0
        for reaction, count in items.items():
            content.append(f"`{count:>2}` ... **{reaction}**")
            total += count
        if len(content) == 0:
            content.append("Nothing yet")

        embed.add_field(name=f"{total} in total", value="\n".join(content))
        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)

    @reactions.group(name="add", aliases=["edit"])
    async def reactions_add(self, ctx):
        """Add reaction trigger"""
        await utils.send_help(ctx)

    @reactions_add.command(name="text")
    async def reactions_add_text(
        self, ctx, name: str, match: str, trigger: str, response: str, *, comment: str = None
    ):
        """Add text reaction

        name: "Reaction name"
        match: [full | any | starts | ends]
        trigger: "Trigger string" (in quotes)
        response: "Response string" (in quotes)
        """
        if not self._check_match_string(match):
            await utils.send_help(ctx)

        name = discord.utils.escape_markdown(name)
        if name in self.reactions.keys():
            raise discord.BadArgument("Reaction name already exists")

        self.reactions[name] = {
            "match": match,
            "type": "text",
            "trigger": trigger.lower(),
            "response": response,
            "comment": comment if comment is not None else "",
        }
        self._save_reactions()
        await ctx.send(f"Reaction **{discord.utils.escape_markdown(name)}** added")
        await self.event.sudo(
            ctx.author,
            ctx.channel,
            'New text reaction: `{name}` on "`{trigger}`"'.format(name=name, trigger=trigger),
        )

        await utils.delete(ctx)

    @reactions_add.command(name="image", aliases=["img"])
    async def reactions_add_image(
        self, ctx, name: str, match: str, trigger: str, filename: str, *, comment: str = None
    ):
        """Add multimedia reaction

        name: "Reaction name"
        match: [full | any | starts | ends]
        trigger: "Trigger string" (in quotes)
        filename: Path to an image or a video
        """
        if not self._check_match_string(match):
            return await ctx.send_help(ctx.invoked_with)

        name = discord.utils.escape_markdown(name)
        if name in self.reactions.keys():
            raise discord.BadArgument("Reaction name already exists")

        if not os.path.exists(self.path + filename):
            raise discord.BadArgument("No such image")

        self.reactions[name] = {
            "match": match,
            "type": "image",
            "trigger": trigger.lower(),
            "response": filename,
            "comment": comment if comment is not None else "",
        }
        self._save_reactions()
        await ctx.send(f"Media reaction **{name}** added")
        await self.event.sudo(
            ctx.author,
            ctx.channel,
            "New media reaction: `{name}` on `{trigger}`".format(name=name, trigger=trigger),
        )

        await utils.delete(ctx)

    @reactions_add.command(name="condition", aliases=["cond"])
    async def reactions_add_condition(self, ctx, name: str, type: str, *, ids: str = None):
        """Add condition for a reaction.

        name: Trigger name
        type: [user | channel]
        ids: Space separated IDs; leave blank to remove condition type

        This will overwrite old settings for given condition type.
        """
        if name not in self.reactions:
            raise commands.BadArgument("Reaction name not found")
        if type not in ["user", "channel"]:
            raise commands.BadArgument("Type not supported")
        try:
            ids = [int(i) for i in ids.split(" ")]
        except:
            if ids is not None:
                raise commands.BadArgument("Invalid IDs")

        if ids is None:
            del self.reactions[name][type]
        else:
            self.reactions[name][type] = ids
        self._save_reactions()
        await ctx.send(f"Condition for **{name}** saved")

        # log event
        if ids is None:
            message = f"Reaction condition `{type}` for `{name}` cleared."
        else:
            message = f"Reaction condition for `{name}`: "
            f"{type} has to match {', '.join(ids)}"
        await self.event.sudo(ctx.author, ctx.channel, message)

        await utils.delete(ctx)

    @reactions_add.command(name="comment")
    async def reactions_add_comment(self, ctx, name: str, *, comment: str):
        """Add comment to a reaction

        name: Trigger name
        comment: Text description for a reaction
        """
        if name not in self.reactions:
            raise commands.BadArgument("Name not found")

        self.reactions[name]["comment"] = comment
        self._save_reactions()
        await ctx.send(f"Comment for **{name}** set")

        await utils.delete(ctx)

    @reactions.command(name="remove", aliases=["delete", "rm", "del"])
    async def reactions_remove(self, ctx, name: str):
        """Remove reaction trigger

        name: Trigger name
        """
        if name not in self.reactions:
            raise commands.BadArgument("Name not found")
        del self.reactions[name]
        self._save_reactions()
        return await ctx.send(f"Reaction **{name}** removed")
        await self.event.sudo(ctx.author, ctx.channel, f"Reaction `{name}` removed.")

        await utils.delete(ctx)

    @commands.is_owner()
    @commands.group(name="image", aliases=["img", "images"])
    async def actor_image(self, ctx: commands.Context):
        """Manage images available to the bot"""
        await utils.send_help(ctx)

    @actor_image.command(name="list")
    async def actor_image_list(self, ctx: commands.Context):
        """List available images"""
        files = os.listdir(self.path)

        result = ""
        for f in files:
            if f.split(".")[-1] not in ["jpg", "jpeg", "png", "webm", "mp4", "gif"]:
                continue
            result += f"{f} ({int(os.path.getsize(self.path + f)/1024)} kB)\n"
        if result == "":
            result = "(No images)"
        await ctx.send(f"```\n{result}\n```")

        await utils.delete(ctx)

    @actor_image.command(name="download", aliases=["dl"])
    async def actor_image_download(self, ctx, url: str, filename: str):
        """Download new image

        url: URL of an image
        filename: Target filename
        """
        if filename.split(".")[-1] not in ["jpg", "jpeg", "png", "webm", "mp4", "gif"]:
            return await ctx.send("Please, specify an file extension.")
        if "/" in filename or "\\" in filename or ".." in filename:
            return await ctx.send("Invalid characters inside of filename.")

        with open(self.path + filename, "wb") as f:
            response = get(url)
            f.write(response.content)

        await ctx.send("Image succesfully downloaded")

    @actor_image.command(name="remove", aliases=["delete", "rm", "del"])
    async def actor_image_remove(self, ctx, filename: str):
        """Remove image

        filename: An image file
        """
        if "/" in filename or "\\" in filename or ".." in filename:
            return await ctx.send("Invalid characters inside of filename.")

        os.remove(self.path + filename)
        await ctx.send("File deleted")

        await utils.delete(ctx)

    @actor_image.command(name="show")
    async def actor_image_show(self, ctx, filename: str):
        """Show an image

        filename: An image file
        """
        await self.send_image(ctx, ctx.channel, filename)

        await utils.delete(ctx)

    @commands.cooldown(rate=1, per=600.0, type=commands.BucketType.default)
    @commands.check(check.is_bot_owner)
    @commands.check(check.is_in_modroom)
    @commands.group(name="change")
    async def change(self, ctx: commands.Context):
        """Change the bot"""
        await utils.send_help(ctx)

    @change.command(name="avatar")
    async def change_avatar(self, ctx: commands.Context, path: str):
        """Change bot's avatar"""
        with open(path, "rb") as img:
            avatar = img.read()
            await self.bot.user.edit(avatar=avatar)
            await ctx.send(content="Dobře, takhle teď budu vypadat:", file=discord.File(path))
        await self.event.sudo(ctx.author, ctx.channel, f"New bot avatar set.")

    @change.command(name="name")
    async def change_name(self, ctx: commands.Context, *args):
        """Change bot's name

        name: New name
        """
        name = " ".join(args)
        await self.bot.user.edit(username=name)
        await ctx.send(f"Dobře, od teď jsem **{name}**")
        await self.event.sudo(ctx.author, ctx.channel, f"New bot name set.")


def setup(bot):
    bot.add_cog(Actor(bot))
