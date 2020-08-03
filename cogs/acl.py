from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository import acl_repo

repo_a = acl_repo.ACLRepository()

# TODO Iterate over all command the bot has
#      and send message to botdev if some are not found in database


class ACL(rubbercog.Rubbercog):
    """Permission controll"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.is_owner()
    @commands.group(name="acl")
    async def acl(self, ctx):
        """Permission controll"""
        await utils.send_help(ctx)

    @acl.group(name="group")
    async def acl_group(self, ctx):
        """Group controll"""
        await utils.send_help(ctx)

    @acl_group.command(name="list")
    async def acl_group_list(self, ctx):
        """List ACL groups"""
        # FIXME show as dependencies

        groups = repo_a.getGroups()
        result = ""
        for group in groups:
            if len(result) > 2000:
                await ctx.send(result)
                result = ""
            result += "\n" + (str(group))
        await ctx.send(result)

    @acl_group.command(name="add")
    async def acl_group_add(self, ctx, name: str, role_id: int):
        """Add ACL group

        role_id: Role ID or 0 for DM
        """
        pass

    @acl_group.command(name="remove", aliases=["delete"])
    async def acl_group_remove(self, ctx, id: int):
        """Remove ACL rule

        id: Rule ID
        """
        pass

    @acl.group(name="command")
    async def acl_command(self, ctx):
        """Command controll"""
        await utils.send_help(ctx)

    @acl_command.command(name="add")
    async def acl_command_add(self, ctx, *, command: str):
        """Add command"""
        pass

    @acl_command.command(name="remove", aliases=["delete"])
    async def acl_command_remove(self, ctx, *, command: str):
        """Remove command"""
        pass

    @acl_command.group(name="constraint")
    async def acl_command_constraint(self, ctx):
        """Manage command constraints"""
        await utils.send_help(ctx)

    @acl_command_constraint.command(name="add")
    async def acl_command_constraint_add(
        self, ctx, command: str, constraint: str, id: int, allow: bool
    ):
        """Add command constraint"""
        pass

    @acl_command_constraint.command(name="remove")
    async def acl_command_constraint_remove(self, ctx, command: str, constraint: str, id: int):
        """Remove command constraint"""
        pass


def setup(bot):
    bot.add_cog(ACL(bot))
