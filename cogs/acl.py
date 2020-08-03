from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository import acl_repo

repo_a = acl_repo.ACLRepository()

# TODO Iterate over all command the bot has
#      and send message to botdev if some are not found in database


class ACL(rubbercog.Rubbercog):
    """Permission control"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.is_owner()
    @commands.group(name="acl")
    async def acl(self, ctx):
        """Permission control"""
        await utils.send_help(ctx)

    @acl.group(name="group")
    async def acl_group(self, ctx):
        """Group control"""
        await utils.send_help(ctx)

    @acl_group.command(name="list")
    async def acl_group_list(self, ctx):
        """List ACL groups"""
        # FIXME show as dependencies

        groups = repo_a.getGroups()
        result = ""
        for group in groups:
            if len(result) > 2000:
                await ctx.send(f"```\n{result}```")
                result = ""
            result += "\n" + (group.__repr__())
        if result:
            await ctx.send(f"```\n{result}```")
        else:
            await ctx.send("nothing yet")

    @acl_group.command(name="add")
    async def acl_group_add(self, ctx, name: str, parent_id: int, role_id: int):
        """Add ACL group

        name: string matching `[a-zA-Z_]*`
        parent_id: Parent group; -1 for None
        role_id: Discord role ID, 0 for DM, -1 for None
        """
        # TODO Match name against regex
        result = repo_a.addGroup(name, parent_id, role_id)
        await ctx.send(result)

    @acl_group.command(name="remove", aliases=["delete"])
    async def acl_group_remove(self, ctx, identifier: str):
        """Remove ACL rule

        identifier: Rule ID or name
        """
        try:
            identifier = int(identifier)
        except ValueError:
            pass
        result = repo_a.deleteGroup(identifier)
        await ctx.send("ok" if result else "not found")

    @acl.group(name="command", aliases=["rule"])
    async def acl_command(self, ctx):
        """Command control"""
        await utils.send_help(ctx)

    @acl_command.command(name="get")
    async def acl_command_get(self, ctx, *, command_name: str):
        """See command's policy"""
        command = repo_a.getCommand(command_name)
        if command:
            await ctx.send("```\n" + command.__repr__() + "```")
        else:
            await ctx.send("nothing yet")

    @acl_command.command(name="add")
    async def acl_command_add(self, ctx, *, command: str):
        """Add command"""
        if command not in self.bot.all_commands.keys():
            return await ctx.send("unknown command")
        result = repo_a.addCommand(command)
        await ctx.send(result)

    @acl_command.command(name="remove", aliases=["delete"])
    async def acl_command_remove(self, ctx, *, command: str):
        """Remove command"""
        result = repo_a.deleteCommand(command)
        await ctx.send("ok" if result else "not found")

    @acl_command.group(name="constraint")
    async def acl_command_constraint(self, ctx):
        """Manage command constraints"""
        await utils.send_help(ctx)

    @acl_command_constraint.command(name="add")
    async def acl_command_constraint_add(
        self, ctx, command: str, constraint: str, id: int, allow: bool
    ):
        """Add command constraint

        command: valid command
        constraint: "user" or "group" string
        id: discord user ID or ACL group ID
        allow: True or False
        """
        result = repo_a.setCommandConstraint(
            command=command, constraint=constraint, id=id, allow=allow
        )
        await ctx.send(result)

    @acl_command_constraint.command(name="remove")
    async def acl_command_constraint_remove(self, ctx, command: str, constraint_id: int):
        """Remove command constraint

        command: valid command
        constraint: "user" or "group" string
        constraint_id: Assigned constraint ID
        """
        result = repo_a.removeCommandConstraint(command=command, constraint_id=id)
        await ctx.send(result)


def setup(bot):
    bot.add_cog(ACL(bot))
