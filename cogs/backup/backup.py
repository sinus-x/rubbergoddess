import os
import datetime
import shutil
import json

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import utils, acl

from . import database


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.text = CogText("backup")

    @commands.check(acl.check)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.group(name="backup")
    async def backup(self, ctx):
        """Backup various kinds of data"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @backup.command(name="channel")
    async def backup_channel(self, ctx, channel: discord.TextChannel, limit: int = None):
        """Backup contents of text channel.

        channel: Text channel to be backed up.
        limit: Optional. Number of messages to back up.

        This can only be run once at a time.
        """
        now = datetime.datetime.now()
        database.Information.add(
            id=channel.guild.id,
            channel_id=channel.id,
            author_id=ctx.author.id,
        )
        users = set()

        # download messages
        total = str(limit) if limit is not None else "???"
        status = await ctx.send(self.text.get("channel", "messages", count=0, total=total))

        i = 0
        async for message in channel.history(limit=limit, oldest_first=False):
            try:
                attachments = (
                    ",".join([a.url for a in message.attachments])
                    if len(message.attachments)
                    else None
                )
                embeds = (
                    json.dumps([e.to_dict() for e in message.embeds])
                    if len(message.embeds)
                    else None
                )
                database.Message.add(
                    id=message.id,
                    author_id=message.author.id,
                    text=message.content,
                    attachments=attachments,
                    embeds=embeds,
                )
                users.add(message.author)
                i += 1
            except Exception as exc:
                await ctx.send(exc)

            if i > 0 and i % 500 == 0:
                await status.edit(
                    content=self.text.get("channel", "messages", count=i, total=total)
                )

        # download user information
        await status.edit(content=status.content + " " + self.text.get("channel", "users"))
        for user in users:
            try:
                database.User.add(
                    id=user.id,
                    name=user.name,
                    avatar=await user.avatar_url_as(format="png", size=256).read(),
                )
            except Exception as exc:
                await ctx.send(f"`{exc}`")

        # done
        await status.edit(content=status.content + " " + self.text.get("channel", "done"))

        # get file size in bytes
        dbsize = os.path.getsize("data/backup/default.db")
        if ctx.guild is not None:
            limit = ctx.guild.filesize_limit
        else:
            # exactly 8MB is refused, this is ok
            limit = 8 * 1024 ** 2 - 1024

        # copy
        fname = now.strftime(f"backup_%Y%m%d-%H%M%S_channel-{channel.name}.db")
        fpath = "data/backup/" + fname
        shutil.copy("data/backup/default.db", fpath)

        text = self.text.get("saved_as", file=fpath)
        if dbsize > limit:
            await ctx.send(text + " " + self.text.get("too_big", size=int(dbsize / 1000)))
        else:
            await ctx.send(
                text,
                file=discord.File(fp=fpath, filename=fname),
            )
        database.wipe()

        delta = datetime.datetime.now() - now
        await ctx.send(self.text.get("time", seconds=int(delta.total_seconds())))

    @commands.guild_only()
    @commands.check(acl.check)
    @backup.command(name="emojis")
    async def backup_emojis(self, ctx):
        """Backup guild emojis.

        This can only be run once at a time.
        """
        now = datetime.datetime.now()
        database.Information.add(
            id=ctx.guild.id,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
        )
        database.User.add(
            id=ctx.author.id,
            name=ctx.author.name,
            avatar=await ctx.author.avatar_url_as(format="png", size=256).read(),
        )

        status = await ctx.send(self.text.get("emojis", "downloading", count=len(ctx.guild.emojis)))
        for emoji in ctx.guild.emojis:
            try:
                database.Emoji.add(
                    id=emoji.id,
                    name=emoji.name,
                    data=await emoji.url.read(),
                )
            except Exception as exc:
                await ctx.send(f"`{exc}`")
        await status.edit(content=status.content + " " + self.text.get("emojis", "done"))

        # get file size in bytes
        dbsize = os.path.getsize("data/backup/default.db")

        # copy
        fname = now.strftime(f"backup_%Y%m%d-%H%M%S_emojis-{ctx.guild.name}.db")
        fpath = "data/backup/" + fname
        shutil.copy("data/backup/default.db", fpath)

        text = self.text.get("saved_as", file=fpath)
        if dbsize > ctx.guild.filesize_limit:
            await ctx.send(text + " " + self.text.get("too_big", size=int(dbsize / 1000)))
        else:
            await ctx.send(
                text,
                file=discord.File(fp=fpath, filename=fname),
            )
        database.wipe()

        delta = datetime.datetime.now() - now
        await ctx.send(self.text.get("time", seconds=int(delta.total_seconds())))
