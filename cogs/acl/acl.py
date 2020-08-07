import csv
from typing import List, Optional

import discord
from discord.ext import commands

from core import check, rubbercog, utils
from repository import acl_repo
from repository.database.acl import ACL_rule

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
        # TODO Sort group overrides
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

    ## Security

    @acl.command(name="audit")
    async def acl_audit(self, ctx):
        """Make security audit"""
        rules = repo_a.getRules()
        all_commands = self.get_command_names()

        result = []
        for rule in rules:
            result.append(rule.__repr__())

        not_in_db = len(all_commands) - len(rules)

        output = utils.paginate(result)
        for page in output:
            await ctx.send("```" + page + "```")

        if not_in_db:
            await ctx.send(f"**{not_in_db} commands** are not in database. Run `?acl check`.")

    @acl.command(name="check")
    async def acl_check(self, ctx):
        """Check, if all commands are in database"""
        commands = self.get_free_commands()
        output = utils.paginate(commands)
        if len(output):
            for page in output:
                await ctx.send("```" + page + "```")
            await ctx.send(f"Found **{len(commands)} commands** with no defined behaviour.")
        else:
            await ctx.send("everything is OK.")

    @acl.command(name="init")
    async def acl_init(self, ctx):
        """Load default settings from file"""
        all_commands = self.get_command_names()
        acl_groups = [g.name for g in repo_a.getGroups()]
        skipped = []
        errors = {}
        done = []
        with open("data/acl/commands.csv", newline="") as csvfile:
            reader = csv.reader(csvfile)
            for i, command in enumerate(reader, 1):
                if len(command) != 4:
                    skipped.append(f"{i} (invalid field count) | " + ",".join(command))
                    continue
                if command[0] not in all_commands:
                    skipped.append(f"{i} (command not found) | " + ",".join(command))
                    continue
                if command[1] not in ("0", "1"):
                    skipped.append(f"{i} (invalid default) | " + ",".join(command))
                    continue

                skip = False
                groups_allowed = [g for g in command[2].split(" ") if len(g)]
                for g in groups_allowed:
                    if g not in acl_groups:
                        skipped.append(f"{i} (invalid allow group) | " + ",".join(command))
                        skip = True
                        break
                if skip:
                    continue
                groups_denied = [g for g in command[3].split(" ") if len(g)]
                for g in groups_denied:
                    if g not in acl_groups:
                        skipped.append(f"{i} (invalid deny group)  | " + ",".join(command))
                        skip = True
                        break
                if skip:
                    continue

                try:
                    repo_a.addRule(command[0], command[1] == "1")
                    for g in groups_allowed:
                        repo_a.addGroupConstraint(
                            command=command[0], identifier=g, allow=True,
                        )
                    for g in groups_denied:
                        repo_a.addGroupConstraint(
                            command=command[0], identifier=g, allow=False,
                        )
                    done.append(command[0])
                except acl_repo.Duplicate as e:
                    skipped.append(f"{i} | {str(e)}")
                except acl_repo.ACLException as e:
                    errors[command[0]] = str(e)

        if len(done):
            await ctx.send("New commands: ```\n" + ", ".join(done) + "```")
        if len(skipped):
            await ctx.send("Skipped CSV file entries:")
            for page in utils.paginate(skipped):
                await ctx.send("```" + page + "```")
        if len(errors):
            await ctx.send("Reported database errors:")
            output = []
            for c, err in errors.items():
                output.append(f"{c}: {err}")
            for page in utils.paginate(output):
                await ctx.send("```" + page + "```")

    ##
    ## Logic
    ##
    def get_command_names(self) -> Optional[List[str]]:
        """Return list of registered commands"""
        result = []
        for command in self.bot.walk_commands():
            result.append(command.qualified_name)
        return result

    def get_free_commands(
        self, *, commands: List[str] = None, rules: List[ACL_rule] = None
    ) -> Optional[List[str]]:
        """Return list of commands not in database"""
        if commands is None:
            commands = self.get_command_names()
        if rules is None:
            rules = repo_a.getRules()

        for rule in rules:
            if rule.command in commands:
                commands.remove(rule.command)
        return commands
