import datetime
import requests
import tempfile

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from repository.anonsend_repo import AnonsendRepository

repo_a = AnonsendRepository()


class Anonsend(rubbercog.Rubbercog):
    """Send files anonymously"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("anonsend")
        self.config = CogConfig("anonsend")

    @commands.group()
    async def anonsend(self, ctx):
        """Send an image anonymously.

        Run `anonsend link` to get the URL to the website.
        """
        await utils.send_help(ctx)

    @commands.guild_only()
    @commands.check(acl.check)
    @anonsend.command(name="add")
    async def anonsend_add(self, ctx, name: str):
        """Add channel used for anonymous posts"""
        try:
            repo_a.add(guild_id=ctx.guild.id, channel_id=ctx.channel.id, name=name)
        except ValueError:
            return await ctx.send(self.text.get("name_exists"))

        await self.event.sudo(ctx, f"anonsend channel created: `{self.sanitise(name)}`.")
        await ctx.send(self.text.get("added"))

    @commands.check(acl.check)
    @anonsend.command(name="remove")
    async def anonsend_remove(self, ctx, name: str):
        """Remove channel used for anonymous posts"""
        try:
            repo_a.remove(name=name)
        except ValueError:
            return await ctx.send(self.text.get("bad_name"))

        await self.event.sudo(ctx, f"anonsend channel removed: `{self.sanitise(name)}`.")
        await ctx.send(self.text.get("removed"))

    @commands.check(acl.check)
    @anonsend.command(name="rename")
    async def anonsend_rename(self, ctx, old_name: str, new_name: str):
        """Rename anonymous post channel"""
        try:
            repo_a.rename(old_name=str, new_name=str)
        except ValueError as e:
            return await ctx.send("`" + str(e) + "`")

        await self.event.sudo(
            ctx,
            (
                "anonsend channel renamed: "
                f"`{self.sanitise(old_name)}` to "
                f"`{self.sanitise(new_name)}`."
            ),
        )
        await ctx.send(self.text.get("renamed"))

    @commands.guild_only()
    @commands.check(acl.check)
    @anonsend.command(name="list")
    async def anonsend_list(self, ctx):
        """Get mappings for current guild"""
        channels = repo_a.get_all(ctx.guild.id)
        await ctx.send("```\n" + "\n".join([str(x) for x in channels]) + "\n```")

    @commands.check(acl.check)
    @anonsend.command(name="fetch")
    async def anonsend_fetch(self, ctx):
        """Get list of pending files"""
        url_base = self.config.get("url") + "/api.php?apikey=" + self.config.get("apikey")
        response = requests.get(url_base + "&action=list")
        files = response.json()

        embed = self.embed(ctx=ctx, title=self.text.get("fetch_server"))
        for i, (file, timestamp) in enumerate(files.items()):
            uploaded = datetime.datetime.fromtimestamp(timestamp)
            embed.add_field(
                name=file,
                value=uploaded.strftime("%Y-%m-%d %H:%M:%S")
                + "\n"
                + self.text.get(
                    "fetch_age",
                    time=utils.seconds2str((datetime.datetime.now() - uploaded).seconds),
                ),
            )
            if i % 24 == 0 and i > 0:
                await ctx.send(embed=embed)
        await ctx.send(embed=embed)

    @anonsend.command(name="link", aliases=["url"])
    async def anonsend_link(self, ctx):
        """Get link to the anonsend upload website"""
        await ctx.send(self.config.get("url"))

    @commands.dm_only()
    @anonsend.command(name="submit")
    async def anonsend_submit(self, ctx, name: str, filename: str):
        """Send a file"""

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

        url_base = self.config.get("url") + "/api.php?apikey=" + self.config.get("apikey")
        url_base += "&file=" + filename

        # feedback
        message = await ctx.send(self.text.get("downloading"))

        # download image
        response = requests.get(url_base + "&action=download")
        if response.status_code == 404:
            return await ctx.send(self.text.get("bad_filename"))
        if response.status_code != 200:
            await ctx.send(self.text.get("download_error", message=response.content))
            await self.event.error(ctx, "anonsend error: " + response.content)
            return

        image_binary = tempfile.TemporaryFile()
        image_binary.write(response.content)
        image_binary.seek(0)

        # feedback
        await message.edit(content=message.content + " " + self.text.get("uploading"))

        # send it
        await channel.send(
            file=discord.File(
                fp=image_binary,
                filename=filename,
            )
        )
        feedback = requests.get(url_base + "&action=delete")
        if feedback.status_code != 200:
            await self.event.error(ctx, "delete error: " + str(feedback.status_code))

        image_binary.close()

        # feedback
        await message.edit(content=message.content + " " + self.text.get("done"))

        # increment log
        repo_a.increment(name)
        await self.event.user("DMChannel", f"Anonymous image sent to **{self.sanitise(name)}**.")


def setup(bot):
    bot.add_cog(Anonsend(bot))
