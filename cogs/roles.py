import asyncio

import discord
from discord.ext import commands

from core import check, rubbercog
from core.config import config
from repository.subject_repo import SubjectRepository

repo_s = SubjectRepository()

"""
This file should replace react-to-role part of reaction.py in the future.

As it is still in development, we're keeping it in separate branch.


Before running this, you need to alter the subjects table. Open your psql
shell and run:
ALTER TABLE subjects
ADD COLUMN category VARCHAR,
ADD COLUMN name VARCHAR;
"""


class Roles(rubbercog.Rubbercog):
    """Edit the roles"""

    def __init__(self, bot):
        super().__init__(bot)

    ##
    ## Commands
    ##

    @commands.guild_only()
    @commands.check(check.is_native)
    @commands.group(name="subject")
    async def subject(self, ctx):
        """Add or remove subject"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @subject.command(name="add")
    async def subject_add(self, ctx, *, subjects: str):
        """Add subject

        subjects: Space separated subject shortcuts
        """
        # check if all subjects are in database
        shortcuts = discord.utils.escape_markdown(subjects).lower().replace("@", "").split(" ")
        for shortcut in shortcuts:
            if not await self.subject_in_database(ctx=ctx, shortcut=shortcut):
                return

        # edit permissions
        added = False
        for shortcut in shortcuts:
            channel = await self.subject_in_channels(ctx=ctx, shortcut=shortcut)
            if not isinstance(channel, discord.TextChannel):
                return

            # fmt: off
            await self._add_permission(
                ctx=ctx,
                shortcut=shortcut,
                channel=channel,
                permission_type="subject",
            )
            # fmt: on
            added = True

        # add checkmark, wait and delete message
        if added:
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(config.get("delay", "success"))

        await self.deleteCommand(ctx)

    @subject.command(name="remove")
    async def subject_remove(self, ctx, *, subjects: str):
        """Remove subject

        subjects: Space separated subject shortcuts
        """
        shortcuts = discord.utils.escape_markdown(subjects).lower().replace("@", "").split(" ")
        for shortcut in shortcuts:
            if not await self.subject_in_database(ctx=ctx, shortcut=shortcut):
                return

        # edit permissions
        added = False
        for shortcut in shortcuts:
            channel = await self.subject_in_channels(ctx=ctx, shortcut=shortcut)
            if not isinstance(channel, discord.TextChannel):
                return

            # fmt: off
            await self._remove_permission(
                ctx=ctx,
                shortcut=shortcut,
                channel=channel,
                type="subject",
            )
            # fmt: on
            added = True

        # add checkmark, wait and delete message
        if added:
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(config.get("delay", "success"))

        await self.deleteCommand(ctx)

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        # add reactions if message starts with "role" string or is in role channel
        # fmt: off
        if message.channel.id in config.role_channels \
        or message.content.startswith(config.role_string):
            role_data = await self._emote_role_map(message)
            for emote_channel in role_data:
                await message.add_reaction(emote_channel[0])
        # fmt: on

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # channel
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        # message
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        # author
        author = message.guild.get_member(payload.user_id)
        if author.bot:
            return

        # emoji
        if payload.emoji.is_custom_emoji():
            emoji = self.bot.get_emoji(payload.emoji.id) or payload.emoji
        else:
            emoji = payload.emoji.name

        # check for role string
        if (
            not message.content.startswith(config.role_string)
            and not channel.id in config.role_channels
        ):
            return

        # add role on reaction
        emote_channel_list = await self._emote_role_map(message)
        for emote_channel in emote_channel_list:
            if str(emoji) == emote_channel[0]:
                await self._add_permission(message=message, shortcut=emote_channel[1])
                break
        else:
            await message.remove_reaction(emoji, author)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass

    ##
    ## Helper functions
    ##

    async def subject_in_database(self, *, ctx: commands.Context, shortcut: str):
        """Display error and delete message if shortcut is not valid subject"""
        if repo_s.get(shortcut) is None:
            await ctx.send(
                f"**{shortcut}** is not a subject", delete_after=config.get("delay", "error"),
            )
            await ctx.message.add_reaction("❎")
            await asyncio.sleep(config.get("delay", "error"))
            await self.deleteCommand(ctx)
            return False
        return True

    async def subject_in_channels(self, *, ctx: commands.Context, shortcut: str):
        """Send error if shortcut is not valid channel"""
        channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)
        if channel is None:
            await ctx.send(
                f"Channel for **{shortcut}** does not exist",
                delete_after=config.get("delay", "error"),
            )
            return False
        return channel

    async def _add_permission(
        self,
        *,
        shortcut: str,
        ctx: commands.Context = None,
        message: discord.Message = None,
        channel: discord.TextChannel = None,
        permission_type: str = None,
    ):
        """Add subject channel"""
        # fmt: off
        print(f"""DEBUG:
shortcut:        {shortcut}
ctx:             {ctx}
channel:         {channel}
permission_type: {permission_type}
""")
        # fmt: on

        # source can be context or message
        if ctx is None and message is None:
            return self.console.error("Chameleon:_add_permission", "Missing any context")
        source = ctx if ctx is not None else message

        if channel is None and source is None:
            return self.console.error(
                "Chameleon:_add_permission", "No channel to apply the overrides to"
            )
        elif channel is None:
            channel = discord.utils.get(source.guild.text_channels, name=shortcut)

        # test permission type
        if permission_type not in ["subject", "role", None]:
            return self.console.error("Chameleion:_add_permission", "Wrong permission type")
        if permission_type is None and channel is not None:
            permission_type = "role" if repo_s.get(channel.name) is None else "subject"
        else:
            permission_type = "role"

        # access controll
        if permission_type == "subject":
            # get user roles
            allowed = False
            user_role_ids = [x.id for x in source.author.roles]
            for role_id in user_role_ids:
                if role_id in config.get("roles", "native"):
                    allowed = True
                    break
            if not allowed:
                # deny
                print("DENIED!")
                return
        else:
            role = discord.utils.get(self.getGuild().roles, name=shortcut)
            limit = discord.utils.get(self.getGuild().roles, name="---INTERESTS")
            if role >= limit:
                # TODO denied
                print("DENIED!")
                return

        if permission_type == "subject":
            # add subject channel
            await channel.set_permissions(source.author, view_channel=True)
            print(f"Added to channel {channel.name}")
            # try to add teacher channel
            shortcut = shortcut + config.get("channels", "teacher suffix")
            channel = discord.utils.get(source.guild.text_channels, name=shortcut)
            if channel is not None:
                await channel.set_permissions(source.author, view_channel=True)
                print(f"Added to channel {channel.name}")
        else:
            await source.author.add_roles(role)
            print(f"Added role {role.name}")

    async def _remove_permission(
        self,
        *,
        ctx: commands.Context,
        shortcut: str,
        channel: discord.TextChannel = None,
        permission_type: str = None,
    ):
        """Remove subject channel"""
        pass

    async def _emote_role_map(self, message):
        """Return list of role names and emotes that represent them"""

        # preprocess message content
        content = message.content.replace("**", "")
        try:
            content = content.rstrip().split("\n")
        except ValueError:
            return
            # TODO Send Role help

        # check every line
        result = []
        for i, line in enumerate(content):
            if i == 0 and line == config.get("chameleon", "trigger"):
                continue
            try:
                tokens = line.split(" ")
                emote = tokens[0]
                channel = tokens[1]

                if "<#" in emote:
                    emote = int(emote.replace("<#", "").replace(">", ""))
                result.append([emote, channel])
            except Exception as e:
                # TODO Send "invalid role line"
                print("invalid role line: " + line)
                return
        return result


def setup(bot):
    bot.add_cog(Roles(bot))
