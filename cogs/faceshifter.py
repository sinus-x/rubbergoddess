import discord
from discord.ext import commands

from core import check, rubbercog
from core.config import config
from core.text import text
from repository.subject_repo import SubjectRepository

repo_s = SubjectRepository()


class Faceshifter(rubbercog.Rubbercog):
    """Manage roles and subjects"""

    def __init__(self, bot):
        super().__init__(bot)
        self.limit_programmes = None
        self.limit_interests = None

    ##
    ## Getters
    ##

    def getLimitProgrammes(self, location: discord.abc.Messageable) -> discord.Role:
        if self.limit_programmes is None:
            self.limit_programmes = discord.utils.get(location.guild.roles, name="---PROGRAMMES")
        return self.limit_programmes

    def getLimitInterests(self, location: discord.abc.Messageable) -> discord.Role:
        if self.limit_interests is None:
            self.limit_interests = discord.utils.get(location.guild.roles, name="---INTERESTS")
        return self.limit_interests

    ##
    ## Commands
    ##

    @commands.guild_only()
    @commands.check(check.is_verified)
    @commands.group(name="subject")
    async def subject(self, ctx):
        """Add or remove subject"""
        await self.deleteCommand(ctx)
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

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
                await ctx.send(text.fill(
                    "faceshifter",
                    "not subject",
                    mention=ctx.author.mention,
                    shortcut=subject
                ))
                # fmt: on
            else:
                await self._subject_add(ctx, ctx.author, channel)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

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
                await ctx.send(text.fill(
                    "faceshifter",
                    "not subject",
                    mention=ctx.author.mention,
                    shortcut=subject
                ))
                # fmt: on
            else:
                await self._subject_remove(ctx, ctx.author, channel)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

    @commands.guild_only()
    @commands.check(check.is_verified)
    @commands.group(name="role", aliases=["programme"])
    async def role(self, ctx):
        """Add or remove role"""
        await self.deleteCommand(ctx)
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

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
                await ctx.send(text.fill(
                    "faceshifter",
                    "not role",
                    mention=ctx.author.mention,
                    role=role
                ))
                # fmt: on
            else:
                await self._role_add(ctx, ctx.author, guild_role)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

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
                await ctx.send(text.fill(
                    "faceshifter",
                    "not role",
                    mention=ctx.author.mention,
                    role=role
                ))
                # fmt: on
            else:
                await self._role_remove(ctx, ctx.author, guild_role)
        await ctx.send(ctx.author.mention + " ✅", delete_after=3)

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        # fmt: off
        if message.channel.id in config.get("faceshifter", "react-to-role channels") \
        or message.content.startswith(config.get("faceshifter", "react-to-role prefix")):
            emote_channel_list = await self._message_to_tuple_list(message)
            for emote_channel in emote_channel_list:
                try:
                    await message.add_reaction(emote_channel[0])
                except (discord.errors.Forbidden, discord.errors.HTTPException):
                    continue
        # fmt: on

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        # fmt: off
        message_channel = self.bot.get_channel(payload.channel_id)
        message = await message_channel.fetch_message(payload.message_id)

        if message.channel.id in config.get("faceshifter", "react-to-role channels") \
        or message.content.startswith(config.get("faceshifter", "react-to-role prefix")):
            # make a list of current emotes
            emotes = []
            emote_channel_list = await self._message_to_tuple_list(message)
            for emote_channel in emote_channel_list:
                try:
                    await message.add_reaction(emote_channel[0])
                except (discord.errors.Forbidden, discord.errors.HTTPException):
                    continue
                emotes.append(emote_channel[0])
        # fmt: on

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
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
                    await self._subject_add(message.channel, member, subject)
                    break
                role = await self._get_role(channel, emote_channel[1])
                if role is not None:
                    await self._role_add(message.channel, member, role)
                    break
        else:
            # another emote was added
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
        return discord.utils.get(location.guild.text_channels, name=shortcut)

    async def _get_role(self, location, role: str) -> discord.Role:
        return discord.utils.get(location.guild.roles, name=role)

    async def _message_to_tuple_list(self, message: discord.Message) -> list:
        """Return (emote, channel/role) list"""
        # preprocess message content
        content = message.content.replace("*", "").replace("_", "").replace("#", "")
        try:
            content = content.rstrip().split("\n")
        except ValueError:
            await message.channel.send(text.get("faceshifter", "role help"))
            return

        # check every line
        result = []
        for i, line in enumerate(content):
            if i == 0 and line == config.get("faceshifter", "react-to-role prefix").replace(
                "\n", ""
            ):
                # invoked via message prefix, skip the first line
                continue
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
                if message.channel.id in config.get("faceshifter", "react-to-role channels"):
                    return
                await message.channel.send(
                    text.fill(
                        "faceshifter", "invalid role line", line=self.sanitise(line, limit=50)
                    )
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
        # fmt: off
        if (
            channel.id not in config.get("faceshifter", "react-to-role channels")
            and not message.content.startswith(config.get("faceshifter", "react-to-role prefix"))
        ):
            return
        # fmt: on

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
        location: discord.abc.Messageable,
        member: discord.Member,
        channel: discord.TextChannel,
    ):
        # check permission
        for subject_role in config.get("faceshifter", "subject roles"):
            if subject_role in [r.id for r in member.roles]:
                break
        else:
            # they do not have neccesary role
            await location.send(text.fill("deny subject", mention=member.mention))
            return

        await channel.set_permissions(member, view_channel=True)
        teacher_channel = self._get_teacher_channel(channel)
        if teacher_channel is not None:
            await teacher_channel.set_permissions(member, view_channel=True)

    async def _subject_remove(
        self,
        location: discord.abc.Messageable,
        member: discord.Member,
        channel: discord.TextChannel,
    ):
        # we do not need to check for permissions
        await channel.set_permissions(member, overwrite=None)
        teacher_channel = self._get_teacher_channel(channel)
        if teacher_channel is not None:
            await teacher_channel.set_permissions(member, overwrite=None)

    async def _role_add(
        self, location: discord.abc.Messageable, member: discord.Member, role: discord.Role
    ):
        if role < self.getLimitProgrammes(location) and role > self.getLimitInterests(location):
            # role is programme, check if user has permission
            for programme_role in config.get("faceshifter", "programme roles"):
                if programme_role in [r.id for r in member.roles]:
                    break
            else:
                await location.send(text.fill("faceshifter", "deny role", mention=member.mention))
                return
        elif role < self.getLimitInterests(location):
            # role is below interests limit, continue
            pass
        else:
            # role is limit itself or something above programmes
            await location.send(text.fill("faceshifter", "deny high role", mention=member.mention))
            return

        await member.add_roles(role)

    async def _role_remove(
        self, location: discord.abc.Messageable, member: discord.Member, role: discord.Role
    ):
        if role < self.getLimitProgrammes(location) and role > self.getLimitInterests(location):
            # role is programme, check if user has permission
            for programme_role in config.get("faceshifter", "programme roles"):
                if programme_role in [r.id for r in member.roles]:
                    break
            else:
                await location.send(text.fill("faceshifter", "deny role", mention=member.mention))
                return
        elif role < self.getLimitInterests(location):
            # role is below interests limit, continue
            pass
        else:
            # role is limit itself or something above programmes
            await location.send(text.fill("faceshifter", "deny high role", mention=member.mention))
            return

        await member.remove_roles(role)


def setup(bot):
    bot.add_cog(Faceshifter(bot))
