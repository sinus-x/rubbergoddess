import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from core.config import config
from repository.subject_repo import SubjectRepository

repo_s = SubjectRepository()


class Roles(rubbercog.Rubbercog):
    """Manage roles and subjects"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("roles")
        self.text = CogText("roles")

        self.limit_programmes = {}
        self.limit_interests = {}

    ##
    ## Getters
    ##

    def getLimitProgrammes(self, channel: discord.TextChannel) -> discord.Role:
        gid = str(channel.guild.id)
        if gid not in self.limit_programmes:
            self.limit_programmes[gid] = discord.utils.get(
                channel.guild.roles, name="---PROGRAMMES"
            )
        return self.limit_programmes[gid]

    def getLimitInterests(self, channel: discord.TextChannel) -> discord.Role:
        gid = str(channel.guild.id)
        if gid not in self.limit_interests:
            self.limit_interests[gid] = discord.utils.get(channel.guild.roles, name="---INTERESTS")
        return self.limit_interests[gid]

    ##
    ## Commands
    ##

    @commands.check(acl.check)
    @commands.group(name="subject")
    async def subject(self, ctx):
        """Add or remove subject"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @subject.command(name="add")
    async def subject_add(self, ctx, *, subjects: str):
        """Add subject

        subjects: Space separated subject shortcuts
        """
        subjects = self.sanitise(subjects, limit=200).split(" ")
        for subject in subjects:
            channel = await self._get_subject(ctx, subject)
            if channel is None:
                # fmt: off
                await ctx.send(self.text.get(
                    "not_subject",
                    mention=ctx.author.mention,
                    shortcut=subject
                ), delete_after=config.get("delay", "user error"))
                # fmt: on
            else:
                await self._subject_add(ctx.channel, ctx.author, channel)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

        await utils.delete(ctx)

    @commands.check(acl.check)
    @subject.command(name="remove")
    async def subject_remove(self, ctx, *, subjects: str):
        """Remove subject

        subjects: Space separated subject shortcuts
        """
        subjects = self.sanitise(subjects, limit=200).split(" ")
        for subject in subjects:
            channel = await self._get_subject(ctx, subject)
            if channel is None:
                # fmt: off
                await ctx.send(self.text.get(
                    "not_subject",
                    mention=ctx.author.mention,
                    shortcut=subject
                ), delete_after=config.get("delay", "user error"))
                # fmt: on
            else:
                await self._subject_remove(ctx, ctx.author, channel)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

        await utils.delete(ctx)

    @commands.check(acl.check)
    @commands.group(name="role", aliases=["programme"])
    async def role(self, ctx):
        """Add or remove role"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @role.command(name="add")
    async def role_add(self, ctx, *, roles: str):
        """Add role

        roles: Space separated role shortcuts
        """
        roles = self.sanitise(roles, limit=200).split(" ")
        for role in roles:
            guild_role = await self._get_role(ctx, role)
            if guild_role is None:
                # fmt: off
                await ctx.send(self.text.get(
                    "not_role",
                    mention=ctx.author.mention,
                    role=role
                ), delete_after=config.get("delay", "user error"))
                # fmt: on
            else:
                result = await self._role_add(ctx.channel, ctx.author, guild_role)

        if result:
            await ctx.send(ctx.author.mention + " ✅", delete_after=3)

        await utils.delete(ctx)

    @commands.check(acl.check)
    @role.command(name="remove")
    async def role_remove(self, ctx, *, roles: str):
        """Remove role

        roles: Space separated role shortcuts
        """
        roles = self.sanitise(roles, limit=200).split(" ")
        for role in roles:
            guild_role = await self._get_role(ctx, role)
            if guild_role is None:
                # fmt: off
                await ctx.send(self.text.get(
                    "not_role",
                    mention=ctx.author.mention,
                    role=role
                ), delete_after=config.get("delay", "user error"))
                # fmt: on
            else:
                await self._role_remove(ctx.channel, ctx.author, guild_role)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

        await utils.delete(ctx)

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for react-to-role message"""
        if not isinstance(message.channel, discord.TextChannel):
            return

        if message.channel.id not in self.config.get("r2r_channels"):
            return

        emote_channel_list = await self._message_to_tuple_list(message)

        if emote_channel_list is None:
            # do not throw errors if nothing is found
            return

        for emote_channel in emote_channel_list:
            try:
                await message.add_reaction(emote_channel[0])
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                continue

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        """Listen for react-to-role message changes"""
        if payload.channel_id not in self.config.get("r2r_channels"):
            return

        message_channel = self.bot.get_channel(payload.channel_id)
        message = await message_channel.fetch_message(payload.message_id)

        # make a list of current emotes
        emote_channel_list = await self._message_to_tuple_list(message)
        for emote_channel in emote_channel_list:
            try:
                await message.add_reaction(emote_channel[0])
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                continue

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # extract data from payload
        payload = await self._reaction_payload_to_tuple(payload)
        if payload is None:
            return
        channel, message, member, emoji = payload
        emote_channel_list = await self._message_to_tuple_list(message)
        result = None
        for emote_channel in emote_channel_list:
            if str(emoji) == emote_channel[0]:
                # try both subject and role
                subject = await self._get_subject(channel, emote_channel[1])
                if subject is not None:
                    result = await self._subject_add(message.channel, member, subject)
                    break
                role = await self._get_role(channel, emote_channel[1])
                if role is not None:
                    result = await self._role_add(message.channel, member, role)
                    break
        else:
            # another emote was added
            result = None

        if not result:
            try:
                await message.remove_reaction(emoji, member)
            except:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # extract data from payload
        payload = await self._reaction_payload_to_tuple(payload)
        if payload is None:
            return
        channel, message, member, emoji = payload
        emote_channel_list = await self._message_to_tuple_list(message)
        for emote_channel in emote_channel_list:
            if str(emoji) == emote_channel[0]:
                # try both subject and role
                subject = await self._get_subject(channel, emote_channel[1])
                if subject is not None:
                    await self._subject_remove(message.channel, member, subject)
                    break
                role = await self._get_role(channel, emote_channel[1])
                if role is not None:
                    await self._role_remove(message.channel, member, role)
                    break

    ##
    ## Helper functions
    ##
    async def _get_subject(self, location, shortcut: str) -> discord.TextChannel:
        db_subject = repo_s.get(shortcut)
        if db_subject is not None:
            return discord.utils.get(location.guild.text_channels, name=shortcut)
        return

    async def _get_role(self, location, role: str) -> discord.Role:
        return discord.utils.get(location.guild.roles, name=role)

    async def _message_to_tuple_list(self, message: discord.Message) -> list:
        """Return (emote, channel/role) list"""
        # preprocess message content
        content = message.content.replace("*", "").replace("_", "").replace("#", "")
        try:
            content = content.rstrip().split("\n")
        except ValueError:
            await message.channel.send(self.text.get("role_help"))
            return

        # check every line
        result = []
        for line in content:
            try:
                line_ = line.split(" ")
                emote = line_[0]
                target = line_[1]

                if "<#" in emote:
                    # custom emote, get it's ID
                    emote = int(emote.replace("<#", "").replace(">", ""))
                result.append((emote, target))
            except:
                # do not send errors if message is in #add-* channel
                if message.channel.id in self.config.get("r2r_channels"):
                    return
                await self._send(
                    message.channel,
                    self.text.fill("invalid_role_line", line=self.sanitise(line, limit=50)),
                )
                return
        return result

    async def _reaction_payload_to_tuple(self, payload: discord.RawMessageUpdateEvent) -> tuple:
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

        # halt if not react-to-role message
        if channel.id not in self.config.get("r2r_channels"):
            return

        # member
        member = message.guild.get_member(payload.user_id)
        if member.bot:
            return
        # emoji
        if payload.emoji.is_custom_emoji():
            emoji = self.bot.get_emoji(payload.emoji.id) or payload.emoji
        else:
            emoji = payload.emoji.name

        return channel, message, member, emoji

    def _get_teacher_channel(self, subject: discord.TextChannel) -> discord.TextChannel:
        return discord.utils.get(
            subject.guild.text_channels,
            name=subject.name + config.get("channels", "teacher suffix"),
        )

    ##
    ## Logic
    ##
    async def _subject_add(
        self,
        source: discord.TextChannel,
        member: discord.Member,
        channel: discord.TextChannel,
    ) -> bool:
        # check permission
        for subject_role in self.config.get("subject_roles"):
            if subject_role in [r.id for r in member.roles]:
                break
        else:
            # they do not have neccesary role
            await self._send(source, self.text.get("deny_subject", mention=member.mention))
            return False

        await channel.set_permissions(member, view_channel=True)
        teacher_channel = self._get_teacher_channel(channel)
        if teacher_channel is not None:
            await teacher_channel.set_permissions(member, view_channel=True)
        return True

    async def _subject_remove(
        self,
        source: discord.TextChannel,
        member: discord.Member,
        channel: discord.TextChannel,
    ):
        # we do not need to check for permissions
        await channel.set_permissions(member, overwrite=None)
        teacher_channel = self._get_teacher_channel(channel)
        if teacher_channel is not None:
            await teacher_channel.set_permissions(member, overwrite=None)

    async def _role_add(
        self, channel: discord.TextChannel, member: discord.Member, role: discord.Role
    ) -> bool:
        if role < self.getLimitProgrammes(channel) and role > self.getLimitInterests(channel):
            # role is programme, check if user has permission
            for programme_role in self.config.get("programme_roles"):
                if programme_role in [r.id for r in member.roles]:
                    break
            else:
                await self._send(channel, self.text.get("deny_programme", mention=member.mention))
                return False

            # check if user already doesn't have some programme role
            for user_role in member.roles:
                # fmt: off
                if user_role < self.getLimitProgrammes(channel) \
                and user_role > self.getLimitInterests(channel):
                    await self._send(
                        channel, self.text.get("deny_second_programme", mention=member.mention),
                    )
                    return False
                # fmt: on

        elif role < self.getLimitInterests(channel):
            # role is below interests limit, continue
            pass
        else:
            # role is limit itself or something above programmes
            await self._send(channel, self.text.get("deny_high_role", mention=member.mention))
            return False

        await member.add_roles(role)

        # optionally, hide channel
        if channel.id in self.config.get("r2h_channels"):
            await channel.set_permissions(member, read_messages=False)

        return True

    async def _role_remove(
        self, channel: discord.TextChannel, member: discord.Member, role: discord.Role
    ):
        if role < self.getLimitProgrammes(channel) and role > self.getLimitInterests(channel):
            # role is programme, check if user has permission
            for programme_role in self.config.get("programme_roles"):
                if programme_role in [r.id for r in member.roles]:
                    break
            else:
                await self._send(channel, self.text.get("deny_programme", mention=member.mention))
                return
        elif role < self.getLimitInterests(channel):
            # role is below interests limit, continue
            pass
        else:
            # role is limit itself or something above programmes
            return await self._send(
                channel, self.text.get("deny_high_role", mention=member.mention)
            )

        await member.remove_roles(role)

    async def _send(self, channel: discord.TextChannel, text: str):
        if channel.id in self.config.get("r2r_channels"):
            return

        await channel.send(text, delete_after=config.get("delay", "user error"))
