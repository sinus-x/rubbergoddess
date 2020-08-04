import discord
from discord.ext import commands

from core import check, rubbercog, utils
from repository import acl_repo

repo_a = acl_repo.ACLRepository()

# TODO ?acl check: List commands not in database
#      ?acl import: Import JSON with information to fill into the database
#      ?acl export: Export database into JSON


class ACL(rubbercog.Rubbercog):
    """Permission control"""

    def __init__(self, bot):
        super().__init__(bot)

    ##
    ## Commands
    ##

    @commands.is_owner()
    @commands.group(name="acl")
    async def acl(self, ctx):
        """Permission control"""
        await utils.send_help(ctx)

    ## Groups

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
            group_repr = group.__repr__()
            if len(result) + len(group_repr) > 2000:
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
        parent_id: Parent group; 0 for everyone, -1 for None
        role_id: Discord role ID, 0 for DM, -1 for None
        """
        # TODO Match name against regex
        result = repo_a.addGroup(name, parent_id, role_id)
        await ctx.send(result)

    @acl_group.command(name="edit")
    async def acl_group_edit(self, ctx, id: int, param: str, value):
        """Edit group

        id: Group ID
        param:value
        - name: string
        - parent_id: int
        - role_id:   int
        """
        if param == "name":
            result = repo_a.editGroup(id, name=value)
        elif param == "parent_id":
            result = repo_a.editGroup(id, parent_id=int(value))
        elif param == "role_id":
            result = repo_a.editGroup(id, role_id=int(value))
        else:
            raise discord.BadArgument()

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

    ## Rules

    @acl.group(name="rule")
    async def acl_rule(self, ctx):
        """Command control"""
        await utils.send_help(ctx)

    @acl_rule.command(name="get")
    async def acl_rule_get(self, ctx, *, command_name: str):
        """See command's policy"""
        command = repo_a.getRule(command_name)
        await ctx.send("```\n" + command.__repr__() + "```")

    @acl_rule.command(name="add")
    async def acl_rule_add(self, ctx, *, command: str):
        """Add command"""
        if command not in self.bot.all_commands.keys():
            return await ctx.send("unknown command")
        result = repo_a.addRule(command)
        await ctx.send(result)

    @acl_rule.command(name="remove", aliases=["delete"])
    async def acl_rule_remove(self, ctx, *, command: str):
        """Remove command"""
        result = repo_a.deleteRule(command)
        await ctx.send("ok" if result else "not found")

    ## Constraints

    @acl.group(name="user_constraint", aliases=["constraint_user", "uc"])
    async def acl_user_constraint(self, ctx):
        """Manage command constraints"""
        await utils.send_help(ctx)

    @acl_user_constraint.command(name="add", aliases=["a"])
    async def acl_user_constraint_add(self, ctx, command: str, discord_id: int, allow: bool):
        """Add command constraint

        command: A command
        discord_id: User ID
        allow: True or False
        """
        result = repo_a.addUserConstraint(command=command, discord_id=discord_id, allow=allow)
        await ctx.send(result)

    @acl_user_constraint.command(name="remove", aliases=["r"])
    async def acl_user_constraint_remove(self, ctx, constraint_id: int):
        """Remove command constraint

        constraint_id: User constraint ID
        """
        result = repo_a.removeUserConstraint(constraint_id=constraint_id)
        await ctx.send(result)

    @acl.group(name="group_constraint", aliases=["constraint_group", "gc"])
    async def acl_group_constraint(self, ctx):
        """Manage group command constraints"""
        await utils.send_help(ctx)

    @acl_group_constraint.command(name="add", aliases=["a"])
    async def acl_group_constraint_add(self, ctx, command: str, group: str, allow: str):
        """Add command constraint

        command: A command
        group: ACL group name or ID
        allow: True, False or None
        """
        if allow in ("None", "none"):
            allow = None
        else:
            allow = allow in ("True", "true", "1")

        result = repo_a.addGroupConstraint(command=command, identifier=group, allow=allow)
        await ctx.send(result)

    @acl_group_constraint.command(name="remove", aliases=["r"])
    async def acl_group_constraint_remove(self, ctx, constraint_id: int):
        """Remove command constraint

        command: A command
        constraint_id: Group constraint ID
        """
        result = repo_a.removeGroupConstraint(constraint_id=constraint_id)
        await ctx.send(result)
