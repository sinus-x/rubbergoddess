import tempfile
from io import BytesIO
from PIL import Image, ImageOps

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from repository.anonpost_repo import AnonpostRepository

repo_a = AnonpostRepository()


class Anonpost(rubbercog.Rubbercog):
    """Send files anonymously"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("anonpost")
        self.config = CogConfig("anonpost")

    @commands.check(acl.check)
    @commands.group()
    async def anonpost(self, ctx):
        """Manage anonymous channels"""
        await utils.send_help(ctx)

    @commands.guild_only()
    @commands.check(acl.check)
    @anonpost.command(name="add")
    async def anonpost_add(self, ctx, name: str):
        """Add channel used for anonymous posts"""
        try:
            repo_a.add(guild_id=ctx.guild.id, channel_id=ctx.channel.id, name=name)
        except ValueError:
            return await ctx.send(self.text.get("name exists"))

        await self.event.sudo(ctx, f"Anonpost channel created: `{self.sanitise(name)}`.")
        await ctx.send(self.text.get("added"))

    @commands.check(acl.check)
    @anonpost.command(name="remove")
    async def anonpost_remove(self, ctx, name: str):
        """Remove channel used for anonymous posts"""
        try:
            repo_a.remove(name=name)
        except ValueError:
            return await ctx.send(self.text.get("bad name"))

        await self.event.sudo(ctx, f"Anonpost channel removed: `{self.sanitise(name)}`.")
        await ctx.send(self.text.get("removed"))

    @commands.check(acl.check)
    @anonpost.command(name="rename")
    async def anonpost_rename(self, ctx, old_name: str, new_name: str):
        """Rename anonymous post channel"""
        try:
            repo_a.rename(old_name=str, new_name=str)
        except ValueError as e:
            return await ctx.send("`" + str(e) + "`")

        await self.event.sudo(
            ctx,
            (
                "Anonpost channel renamed: "
                f"`{self.sanitise(old_name)}` to "
                f"`{self.sanitise(new_name)}`."
            ),
        )
        await ctx.send(self.text.get("renamed"))

    @commands.guild_only()
    @commands.check(acl.check)
    @anonpost.command(name="list")
    async def anonpost_list(self, ctx):
        """Get mappings for current guild."""
        channels = repo_a.get_all(ctx.guild.id)
        await ctx.send("```\n" + "\n".join([str(x) for x in channels]) + "\n```")

    # The ACL does not support DMs
    # @commands.check(acl.check)
    @commands.dm_only()
    @commands.command()
    async def anonsend(self, ctx, name: str, spoiler: str = None):
        """Send image anonymously

        `name`: Channel code to send the image to.
        `spoiler`: The `spoiler` string to spoiler the image
        """
        # get channel
        target = repo_a.get(name=name)
        if target is None:
            return await ctx.send(self.text.get("no_channel"))

        channel = self.bot.get_channel(target.channel_id)
        if channel is None:
            return await ctx.send(self.text.get("channel_not_found"))

        guild = self.bot.get_guild(target.guild_id)
        guild_user = guild.get_member(ctx.author.id)
        if guild_user is None:
            return await ctx.send(self.text.get("not_in_guild"))

        # check attachment
        if len(ctx.message.attachments) != 1:
            return await ctx.send(self.text.get("bad_attachments"))

        attachment = ctx.message.attachments[0]
        max_size = self.config.get("max_size")
        if attachment.size > max_size * 1024:
            return await ctx.send(self.text.get("attachment_too_big", size=max_size))

        # feedback
        message = await ctx.send(self.text.get("downloading"))

        # download image
        image_bytes = BytesIO()
        await attachment.save(image_bytes)
        try:
            image = Image.open(image_bytes)
        except OSError:
            return await ctx.send(self.text.get("not_image"))

        # fix rotation
        image = ImageOps.exif_transpose(image)

        # feedback
        await message.edit(content=message.content + " " + self.text.get("uploading"))

        # send it
        image_binary = tempfile.TemporaryFile()
        image.convert("RGB").save(image_binary, "JPEG")
        image_binary.seek(0)
        await channel.send(
            file=discord.File(
                fp=image_binary,
                filename="anonymous.jpg",
                spoiler=(spoiler == "spoiler"),
            )
        )
        image_binary.close()

        # feedback
        await message.edit(content=message.content + " " + self.text.get("done"))

        # increment log
        anonchannel = repo_a.increment(name)
        await self.event.user("DMChannel", f"Anonymous image sent to **{self.sanitise(name)}**.")


def setup(bot):
    """Load cog"""
    bot.add_cog(Anonpost(bot))
