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

    def getLimitProgrammes(self, ctx: commands.Context) -> discord.Role:
        if self.limit_programmes is None:
            self.limit_programmes = discord.utils.get(ctx.guild.roles, name="---PROGRAMMES")
        return self.limit_programmes

    def getLimitInterests(self, ctx: commands.Context) -> discord.Role:
        if self.limit_interests is None:
            self.limit_interests = discord.utils.get(ctx.guild.roles, name="---INTERESTS")
        return self.limit_interests

    ##
    ## Commands
    ##

    @commands.guild_only()
    @commands.check(check.is_verified)
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
        subjects = self.sanitise(subjects, limit=200).lower().split(" ")
        for subject in subjects:
            channel = await self._get_subject(ctx, subject)
            if channel is None:
                await ctx.send("předmětovou místnost {subject} tu nemáme.")
            else:
                await self._subject_add(ctx, ctx.author, channel)

        await ctx.send("hotovo ^.^")

    @subject.command(name="remove")
    async def subject_remove(self, ctx, *, subjects: str):
        """Remove subject

        subjects: Space separated subject shortcuts
        """
        subjects = self.sanitise(subjects, limit=200).lower().split(" ")
        for subject in subjects:
            channel = await self._get_subject(ctx, subject)
            if channel is None:
                await ctx.send("předmětovou místnost {subject} tu nemáme.")
            else:
                await self._subject_remove(ctx, ctx.author, channel)

        await ctx.send("hotovo ^.^")

    @commands.guild_only()
    @commands.check(check.is_verified)
    @commands.group(name="role", aliases=["programme"])
    async def role(self, ctx):
        """Add or remove role"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @role.command(name="add")
    async def role_add(self, ctx, *, roles: str):
        """Add role

        roles: Space separated role shortcuts
        """
        pass

    @role.command(name="remove")
    async def role_remove(self, ctx, *, roles: str):
        """Remove role

        roles: Space separated role shortcuts
        """
        pass

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass

    ##
    ## Helper functions
    ##
    async def _get_role(self, ctx, role: str) -> discord.Role:
        pass

    async def _get_subject(self, ctx, shortcut: str) -> discord.TextChannel:
        return discord.utils.get(ctx.guild.text_channels, name=shortcut)

    async def _message_to_tuple(self, message: discord.Message) -> tuple:
        pass

    async def _reaction_payload_to_tuple(self, payload: discord.RawMessageUpdateEvent) -> tuple:
        # _parsePayload()
        pass

    ##
    ## Logic
    ##
    async def _subject_add(self, ctx, member: discord.Member, channel: discord.TextChannel):
        # check permission
        for subject_role in config.get("faceshifter", "subject roles"):
            if subject_role in [r.id for r in member.roles]:
                break
        else:
            # they do not have neccesary role
            await ctx.send("na to nemáš právo ^.^")
            return

        await channel.set_permissions(member, view_channel=True)

    async def _subject_remove(self, ctx, member: discord.Member, channel: discord.TextChannel):
        # we do not need to check for permissions
        await channel.set_permissions(member, overwrite=None)

    async def _role_add(self, ctx, member: discord.Member, role: discord.Role):
        pass

    async def _role_remove(self, ctx, member: discord.Member, role: discord.Role):
        pass


def setup(bot):
    bot.add_cog(Faceshifter(bot))
