import os
import shutil
import json

import discord
from discord.ext import commands

from core import utils, acl

from . import database


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(acl.check)
    @commands.group(name="backup")
    async def backup(self, ctx):
        """Backup various kinds of data"""
        await utils.send_help(ctx)

    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.check(acl.check)
    @backup.command(name="channel")
    async def backup_channel(self, ctx, channel: discord.TextChannel, limit: int = None):
        """Backup contents of text channel.

        channel: Text channel to be backed up.
        limit: Optional. Number of messages to back up.
        """
        database.Information.add(
            guild_id=channel.guild.id,
            channel_id=channel.id,
            author_id=ctx.author.id,
        )
        users = set()

        status = await ctx.send("Downloading... ")

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
                    message_id=message.id,
                    author_id=message.author.id,
                    text=message.content,
                    attachments=attachments,
                    embeds=embeds,
                )
                users.add(message.author)
                i += 1
            except Exception as exc:
                await ctx.send(exc)

            if i > 0 and i % 200 == 0:
                await status.edit(content=status.content[-1900:] + f"{i}... ")

        await status.edit(content=status.content[-1900:] + "And the users... ")

        for user in users:
            database.User.add(
                user_id=user.id,
                name=user.name,
                avatar=await user.avatar_url_as(format="png", size=256).read(),
            )

        await status.edit(content=status.content[-1900:] + "Done.")

        # get file size in bytes
        dbsize = os.path.getsize("data/backup/default.db")
        limit = 0
        if ctx.guild is not None:
            limit = ctx.guild.filesize_limit
        else:
            limit = 8 * 1024 ** 2

        # copy
        fname = f"{ctx.message.id}_backup-{channel.id}.db"
        fpath = "data/backup/" + fname
        shutil.copy("data/backup/default.db", fpath)

        if dbsize >= limit:
            await ctx.send(f"File too big to send, saved as **{fpath}**.")
        else:
            await ctx.send(file=discord.File(fp=fpath, filename=fname))
        database.wipe()
