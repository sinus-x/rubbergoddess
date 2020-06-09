import asyncio

import discord
from discord.ext import commands

from core import check, rubbercog
from core.config import config
from core.text import text
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


class Chameleon(rubbercog.Rubbercog):
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

            # permissions are handled in the _add_permission() funcion

            # fmt: off
            await self._add_permission(
                ctx=ctx,
                member=ctx.author,
                shortcut=shortcut,
                channel=channel,
                permission_type="subject",
            )
            # fmt: on
            added = True

        # add reaction, wait and delete message
        if added:
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(config.get("delay", "success"))
        else:
            await ctx.message.add_reaction("❎")
            await asyncio.sleep(config.get("delay", "user error"))
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

            # permissions are handled in the _remove_permission() funcion

            # fmt: off
            await self._remove_permission(
                ctx=ctx,
                member=ctx.author,
                shortcut=shortcut,
                channel=channel,
                type="subject",
            )
            # fmt: on
            added = True

        # add reaction, wait and delete message
        if added:
            await ctx.message.add_reaction("✅")
            await asyncio.sleep(config.get("delay", "success"))
        else:
            await ctx.message.add_reaction("❎")
            await asyncio.sleep(config.get("delay", "user error"))
        await self.deleteCommand(ctx)

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        # add reactions if message starts with "Role" string or is in role channel
        # fmt: off
        if message.channel.id in config.role_channels \
        or message.content.startswith(config.get("chameleon", "trigger")):
            message_data = await self._emote_role_map(message)
            for emote_channel in message_data:
                await message.add_reaction(emote_channel[0])
        # fmt: on

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # extract data from payload
        payload = await self._parsePayload(payload)
        if payload is None:
            return
        channel, message, member, emoji = payload

        # add role on reaction
        emote_channel_list = await self._emote_role_map(message)
        for emote_channel in emote_channel_list:
            if str(emoji) == emote_channel[0]:
                # fmt: off
                await self._add_permission(
                    message=message,
                    member=member,
                    shortcut=emote_channel[1],
                )
                # fmt: on
                break
        else:
            try:
                await message.remove_reaction(emoji, member)
            except:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # extract data from payload
        payload = await self._parsePayload(payload)
        if payload is None:
            return
        channel, message, member, emoji = payload

        # remove role on reaction
        emote_channel_list = await self._emote_role_map(message)
        for emote_channel in emote_channel_list:
            if str(emoji) == emote_channel[0]:
                # fmt: off
                await self._remove_permission(
                    message=message,
                    member=member,
                    shortcut=emote_channel[1],
                )
                # fmt: on
                break

    ##
    ## Helper functions
    ##

    async def subject_in_database(self, *, ctx: commands.Context, shortcut: str):
        """Display error and delete message if shortcut is not valid subject"""
        if repo_s.get(shortcut) is None:
            await ctx.send(
                text.fill(
                    "chameleon",
                    "shortcut not subject",
                    mention=ctx.author.mention,
                    shortcut=self.sanitise(shortcut, limit=50),
                ),
                delete_after=config.get("delay", "user error"),
            )
            await ctx.message.add_reaction("❎")
            await asyncio.sleep(config.get("delay", "user error"))
            await self.deleteCommand(ctx)
            return False
        return True

    async def subject_in_channels(self, *, ctx: commands.Context, shortcut: str):
        """Send error if shortcut is not valid channel"""
        channel = discord.utils.get(ctx.guild.text_channels, name=shortcut)
        if channel is None:
            await ctx.send(
                text.fill(
                    "chameleon",
                    "shortcut no channel",
                    mention=ctx.author.mention,
                    shortcut=self.sanitise(shortcut, limit=20),
                ),
                delete_after=config.get("delay", "user error"),
            )
            return False
        return channel

    async def _parsePayload(self, payload):
        """Return (channel, message, member, emoji) or None"""
        # channel
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        # message
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        # reacting user
        member = message.guild.get_member(payload.user_id)
        if member.bot:
            return
        # emoji
        if payload.emoji.is_custom_emoji():
            emoji = self.bot.get_emoji(payload.emoji.id) or payload.emoji
        else:
            emoji = payload.emoji.name
        # role string
        if (
            not message.content.startswith(config.get("chameleon", "trigger"))
            and channel.id not in config.role_channels
        ):
            return

        # done
        return channel, message, member, emoji

    async def _add_permission(
        self,
        *,
        shortcut: str,
        member: discord.Member,
        ctx: commands.Context = None,
        message: discord.Message = None,
        channel: discord.TextChannel = None,
        permission_type: str = None,
    ):
        """Add subject channel"""

        # source can be context or message
        if ctx is None and message is None:
            return self.console.error("Chameleon", "Missing any context")
        source = ctx if ctx is not None else message

        if channel is None and source is None:
            self.console.error("Chameleon", "No channel to apply the overrides to")
            return
        elif channel is None:
            channel = discord.utils.get(source.guild.text_channels, name=shortcut)

        # test permission type
        if permission_type not in ["subject", "role", None]:
            return self.console.error("Chameleon", "Wrong permission type")
        if permission_type is None and channel is not None:
            permission_type = "role" if repo_s.get(channel.name) is None else "subject"
        else:
            permission_type = "role"

        # access controll
        if permission_type == "subject":
            # get user roles
            allowed = False
            user_role_ids = [x.id for x in member.roles]
            for role_id in user_role_ids:
                if role_id in config.get("roles", "native"):
                    allowed = True
                    break
            if not allowed:
                await source.channel.send(
                    text.fill("chameleon", "deny subject", mention=member.mention)
                )
                return
        elif permission_type == "role":
            role = discord.utils.get(self.getGuild().roles, name=shortcut)
            limit = discord.utils.get(self.getGuild().roles, name="---INTERESTS")
            if role >= limit:
                await source.channel.send(
                    text.fill("chameleon", "deny role add", mention=member.mention)
                )
                return

        # add
        if permission_type == "subject":
            # add subject channel
            await channel.set_permissions(member, view_channel=True)
            self.console.debug("Chameleon", f"Allowed {member.name} into {channel.name}")
            # try to add teacher channel
            shortcut = shortcut + config.get("channels", "teacher suffix")
            channel = discord.utils.get(source.guild.text_channels, name=shortcut)
            if channel is not None:
                await channel.set_permissions(member, view_channel=True)
                self.console.debug("Chameleon", f"Allowed {member.name} into {channel.name}")

        elif permission_type == "role":
            await member.add_roles(role)
            self.console.debug("Chameleon", f"Added role {role.name} to {member.name}")

    async def _remove_permission(
        self,
        *,
        ctx: commands.Context = None,
        message: discord.Message = None,
        member: discord.Member,
        shortcut: str,
        channel: discord.TextChannel = None,
        permission_type: str = None,
    ):
        """Remove subject channel"""
        # Removing role is easier than adding -- we generally do not need
        # to check permissions. If they want to leave, why not?
        # We only have to check if the role is lower than "---INTERESTS";
        # subject can be _removed_ by anyone.

        # source can be context or message
        if ctx is None and message is None:
            return self.console.error("Chameleon", "Missing any context")
        source = ctx if ctx is not None else message

        if channel is None and source is None:
            return self.console.error("Chameleon", "No channel to apply the overrides to")
        elif channel is None:
            channel = discord.utils.get(source.guild.text_channels, name=shortcut)

        # permission type
        if permission_type not in ["subject", "role", None]:
            return self.console.error("Chameleon", "Wrong permission type")
        if permission_type is None and channel is not None:
            permission_type = "role" if repo_s.get(channel.name) is None else "subject"
        else:
            permission_type = "role"

        # access control
        if permission_type == "role":
            role = discord.utils.get(self.getGuild().roles, name=shortcut)
            limit = discord.utils.get(self.getGuild().roles, name="---INTERESTS")
            if role not in member.roles:
                return
            if role >= limit:
                await source.channel.send(
                    text.fill("chameleon", "deny role remove", mention=member.mention)
                )
                return

        # remove
        if permission_type == "subject":
            # remove subject channel
            await channel.set_permissions(member, overwrite=None)
            self.console.debug("Chameleon", f"Disallowed {member.name} into {channel.name}")
            # try to remove from teacher channel
            shortcut = shortcut + config.get("channels", "teacher suffix")
            channel = discord.utils.get(source.guild.text_channels, name=shortcut)
            if channel is not None:
                await channel.set_permissions(member, overwrite=None)
                self.console.debug("Chameleon", f"Disallowed {member.name} into {channel.name}")

        elif permission_type == "role":
            await member.remove_roles(role)
            self.console.debug("Chameleon", f"Removed role {role.name} from {member.name}")

    async def _emote_role_map(self, message):
        """Return (role name, emote) list"""

        # preprocess message content
        content = message.content.replace("**", "")
        try:
            content = content.rstrip().split("\n")
        except ValueError:
            await message.channel.send(text.get("chameleon", "role help"))
            return

        # check every line
        result = []
        for i, line in enumerate(content):
            if i == 0 and line == config.get("chameleon", "trigger").replace("\n", ""):
                continue
            try:
                tokens = line.split(" ")
                emote = tokens[0]
                channel = tokens[1]

                if "<#" in emote:
                    emote = int(emote.replace("<#", "").replace(">", ""))
                result.append((emote, channel))
            except:
                await message.channel.send(
                    text.fill("chameleon", "invalid role line", line=self.sanitise(line, limit=50))
                )
                return
        return result


def setup(bot):
    bot.add_cog(Chameleon(bot))
