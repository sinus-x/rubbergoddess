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

    @acl.group(name="group", aliases=["g"])
    async def acl_group(self, ctx):
        """Group control"""
        await utils.send_help(ctx)

    @acl_group.command(name="list")
    async def acl_group_list(self, ctx):
        """List ACL groups"""
        groups = repo_a.getGroups()

        if not len(groups):
            return await ctx.send("nothing yet")

        # prepare objects
        for group in groups:
            group.children = []
            group.level = 0

        # fill children and intendation level
        for group in groups:
            if group.parent_id > 0:
                parent = groups[group.parent_id - 1]
                parent.children.append(group)
                group.level = parent.level + 1

        def bfs(queue):
            visited = []
            while queue:
                group = queue.pop(0)
                if group not in visited:
                    visited.append(group)
                    queue = group.children + queue
            return visited

        result = ""
        template = "{group_id:<2} {name:<20} {role:<18}"
        for group in bfs(groups):
            result += "\n" + template.format(
                group_id=group.id, name="  " * group.level + group.name, role=group.role_id,
            )

        await ctx.send("```" + result + "```")

    @acl_group.command(name="add", aliases=["a"])
    async def acl_group_add(self, ctx, name: str, parent_id: int, role_id: int):
        """Add ACL group

        name: string matching `[a-zA-Z_]*`
        parent_id: parent group ID
        role_id: Discord role ID

        To set up virtual group with no link to discord roles, fill in garbage number for role_id.
        To have the group inherit from @everyone/default behaviour, set parent_id to 0.
        """
        # TODO Match name against regex
        result = repo_a.addGroup(name, parent_id, role_id)
        await ctx.send(result)

    @acl_group.command(name="edit", aliases=["e"])
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

    @acl_group.command(name="remove", aliases=["delete", "r"])
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

    @acl_rule.group(name="default")
    async def acl_rule_default(self, ctx):
        """Set default response"""
        await utils.send_help(ctx)

    @acl_rule_default.command(name="allow")
    async def acl_rule_default_allow(self, ctx, *, command: str):
        """Allow by default"""
        result = repo_a.editRule(command=command, allow=True)
        await ctx.send(result)

    @acl_rule_default.command(name="disallow")
    async def acl_rule_default_disallow(self, ctx, *, command: str):
        """Disallow by default"""
        result = repo_a.editRule(command=command, allow=False)
        await ctx.send(result)

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
        await ctx.send("ok" if result else "not found")

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
        await ctx.send("ok" if result else "not found")
