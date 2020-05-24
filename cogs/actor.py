import json
import os

import discord
from discord.ext import commands
from requests import get

from core import check, rubbercog
from core.config import config
from core.emote import emote
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        for r in self.reactions:
            # fmt: off
            if r["match"] == "F" and r["trigger"] == message.content \
            or r["match"] == "A" and r["trigger"] in message.content \
            or r["match"] == "S" and message.content.startswith(r["trigger"]) \
            or r["match"] == "E" and message.content.endswith(r["trigger"]):
                return await message.channel.send(r["response"])
            # fmt: on

    def _save_reactions(self):
        with open(self.reactions_path, "w", encoding="utf-8") as f:
            json.dump(self.reactions, f, ensure_ascii=False, indent=4)

    @commands.group(name="send")
    @commands.check(check.is_bot_owner)
    async def send(self, ctx: commands.Context):
        """Send post to a channel"""
        await self.deleteCommand(ctx)
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
            return await ctx.send_help(ctx.invoked_with)

        await channel.send(text)

    @send.command(name="image")
    async def send_image(self, ctx: commands.Context, channel: discord.TextChannel, filename):
        """Send an image as a bot

        channel: Target text channel
        filename: A filename
        """
        if channel is None or text is None:
            return await ctx.send_help(ctx.invoked_with)

        try:
            await channel.send(file=discord.File(self.path + filename))
        except Exception as e:
            await self.throwError(ctx, "Could not send image", e)

    @commands.group(name="actor")
    @commands.check(check.is_mod)
    async def actor(self, ctx: commands.Context):
        """Send post to a text channel"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @actor.command(name="list")
    async def actor_list(self, ctx: commands.Context):
        """See current reactions"""
        result = ""
        for r in self.reactions:
            s = f"[{r['match']}] {r['trigger']} -> {r['response']}"
            if r["type"] == "image":
                s += " (image)"
            result += s + "\n"

        if len(result) == 0:
            result = "(No reactions)"

        await ctx.send(f"```\n{result}\n```")
        await self.deleteCommand(ctx)

    @commands.is_owner()
    @actor.group(name="text")
    async def actor_text(self, ctx: commands.Context):
        """Manage automatic responses"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @actor_text.command(name="add")
    async def actor_text_add(self, ctx: commands.Context, match: str, trigger: str, response: str):
        """Add text reaction

        match: [full | any | starts | ends]
        trigger: "Trigger string" (in quotes)
        response: "Response string" (in quotes)
        """
        await self.deleteCommand(ctx)

        if match not in ["full", "any", "starts", "ends"]:
            return await ctx.send_help(ctx.invoked_with)

        if trigger in [x["trigger"] for x in self.reactions]:
            return await ctx.send("Trigger already in use")

        self.reactions.append(
            {"match": match[:1].upper(), "type": "T", "trigger": trigger, "response": response}
        )
        self._save_reactions()
        await ctx.send("Reaction added")

    @actor_text.command(name="remove")
    async def actor_text_remove(self, ctx: commands.Context, trigger: str):
        """Remove text reaction"""
        await self.deleteCommand(ctx)

        for r in self.reactions:
            if r["trigger"] == trigger:
                self.reactions.remove(r)
                return await ctx.send("Reaction removed")
        return await ctx.send("Trigger not found")

    @commands.is_owner()
    @actor.group(name="image")
    async def actor_image(self, ctx: commands.Context):
        """Manage images available to the bot"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)
            await self.deleteCommand(ctx)
            return

    @actor_image.command(name="list")
    async def actor_image_list(self, ctx: commands.Context):
        """List available images"""
        files = os.listdir(self.path)

        result = ""
        for f in files:
            if f.split(".")[-1] not in ["jpg", "jpeg", "png", "webm", "mp4"]:
                continue
            result += f"{f} ({int(os.path.getsize(self.path + f)/1024)} kB)\n"
        if result == "":
            result = "(No images)"
        await ctx.send(f"```\n{result}\n```")

    @actor_image.command(name="download", aliases=["dl"])
    async def actor_image_download(self, ctx, url: str, filename: str):
        """Download new image

        url: URL of an image
        filename: Target filename
        """
        if filename.split(".")[-1] not in ["jpg", "jpeg", "png", "webm", "mp4"]:
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

    @actor_image.command(name="show")
    async def actor_image_show(self, ctx, filename: str):
        """Show an image

        filename: An image file
        """
        await self.send_image(ctx, ctx.channel, filename)

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
        with open(path, "rb") as img:
            avatar = img.read()
            await self.bot.user.edit(avatar=avatar)
            await ctx.send(content="Dobře, takhle teď budu vypadat:", file=discord.File(path))

    @change.command(name="name")
    async def change_name(self, ctx: commands.Context, *args):
        """Change bot's name

        name: New name
        """
        name = " ".join(args)
        await self.bot.user.edit(username=name)
        await ctx.send(f"Dobře, od teď jsem **{name}**")

    @change.command(name="activity")
    async def change_activity(self, ctx: commands.Context, type: str, name: str):
        """Change bot's activity

        type: streaming, playing, listening
        name: The activity name
        """
        await self.throwNotification(ctx, text.get("error", "not implemented"))
        await self.deleteCommand(ctx)


def setup(bot):
    bot.add_cog(Actor(bot))
