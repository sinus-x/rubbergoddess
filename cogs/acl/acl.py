import os
import csv
from typing import List, Optional
from datetime import datetime

import discord
from discord.ext import commands

from core import check, rubbercog, utils
from cogs.resource import CogText
from repository import acl_repo
from repository.database.acl import ACL_rule, ACL_group

repo_a = acl_repo.ACLRepository()


class ACL(rubbercog.Rubbercog):
    """Permission control"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("acl")

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
            return await ctx.send(self.text.get("group_list", "nothing"))

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
                group_id=group.id,
                name="  " * group.level + group.name,
                role=group.role_id,
            )

        await ctx.send("```" + result + "```")

    @acl_group.command(name="get")
    async def acl_group_get(self, ctx, identifier: str):
        """Get ACL rule

        identifier: Rule ID or name
        """
        try:
            identifier = int(identifier)
        except ValueError:
            pass
        result = repo_a.getGroup(identifier)
        await ctx.send(self.get_group_representation(ctx.guild, result))

    @acl_group.command(name="add", aliases=["a"])
    async def acl_group_add(self, ctx, name: str, parent_id: int, role_id: int):
        """Add ACL group

        name: string matching `[a-zA-Z_]*`
        parent_id: parent group ID
        role_id: Discord role ID

        To unlink the group from any parents, set parent_id to 0.
        To set up virtual group with no link to discord roles, set role_id to 0.
        """
        # TODO Match name against regex
        result = repo_a.addGroup(name, parent_id, role_id)
        await ctx.send(self.get_group_representation(ctx.guild, result))

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

        await ctx.send(self.get_group_representation(ctx.guild, result))

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
        await ctx.send(
            self.text.get("group_remove", "ok") if result else self.text.get("group_remove", "nothing")
        )

    ## Rules

    @acl.group(name="rule")
    async def acl_rule(self, ctx):
        """Command control"""
        await utils.send_help(ctx)

    @acl_rule.command(name="get")
    async def acl_rule_get(self, ctx, command: str):
        """See command's policy"""
        rule = repo_a.getRule(command)
        await ctx.send("```\n" + self.get_rule_representation(rule) + "```")

    @acl_rule.command(name="add")
    async def acl_rule_add(self, ctx, command: str):
        """Add command"""
        if command not in self.get_command_names():
            return await ctx.send(self.text.get("rule_add", "nothing"))
        result = repo_a.addRule(command)
        await ctx.send("```" + self.get_rule_representation(result) + "```")

    @acl_rule.command(name="remove", aliases=["delete"])
    async def acl_rule_remove(self, ctx, *, command: str):
        """Remove command"""
        result = repo_a.deleteRule(command)
        await ctx.send(
            self.text.get("rule_remove", "ok") if result else self.text.get("rule_remove", "nothing")
        )

    @acl_rule.command(name="flush")
    async def acl_rule_flush(self, ctx):
        """Remove all commands"""
        result = repo_a.deleteAllRules()
        await ctx.send(self.text.get("rule_flush", count=result))

    ## Constraints

    @acl_rule.command(name="default")
    async def acl_rule_default(self, ctx, command: str, allow: bool):
        """Set default response"""
        result = repo_a.editRule(command=command, allow=allow)
        await ctx.send("```" + self.get_rule_representation(result) + "```")

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
        await ctx.send("```" + self.get_rule_representation(result) + "```")

    @acl_user_constraint.command(name="remove", aliases=["r"])
    async def acl_user_constraint_remove(self, ctx, constraint_id: int):
        """Remove command constraint

        constraint_id: User constraint ID
        """
        result = repo_a.removeUserConstraint(constraint_id=constraint_id)
        await ctx.send(
            self.text.get("user_constraint", "removed")
            if result
            else self.text.get("user_constraint", "nothing")
        )

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

        try:
            result = repo_a.addGroupConstraint(command=command, identifier=group, allow=allow)
            await ctx.send("```" + self.get_rule_representation(result) + "```")
        except acl_repo.ACLException as e:
            await ctx.send(str(e))

    @acl_group_constraint.command(name="remove", aliases=["r"])
    async def acl_group_constraint_remove(self, ctx, constraint_id: int):
        """Remove command constraint

        command: A command
        constraint_id: Group constraint ID
        """
        result = repo_a.removeGroupConstraint(constraint_id=constraint_id)
        await ctx.send(
            self.text.get("group_constraint", "removed")
            if result
            else self.text.get("group_constraint", "nothing")
        )

    ## Security

    @acl.command(name="audit")
    async def acl_audit(self, ctx, search: str = None):
        """Make security audit

        search: Only display commands containing the `search` string
        """
        rules = repo_a.getRules()
        if search is not None:
            rules = [r for r in rules if search in r.command]

        result = []
        for rule in sorted(rules, key=lambda r: r.command):
            result.append(self.get_rule_representation(rule))

        output = utils.paginate(result)
        for page in output:
            if len(page):
                await ctx.send("```" + page + "```")

        await ctx.send(self.text.get("audit"))

    @acl.command(name="check")
    async def acl_check(self, ctx):
        """Check, if all commands are in database"""
        commands = self.get_free_commands()
        output = utils.paginate(commands)
        for page in output:
            if len(page):
                await ctx.send("```" + page + "```")
        if len(commands):
            await ctx.send(self.text.get("check", "some", count=len(commands)))
        else:
            await ctx.send(self.text.get("check", "none"))

    ## Import & Export

    @acl.command(name="init")
    async def acl_init(self, ctx):
        """Load default settings from file"""
        now = datetime.now()

        await self.import_csv(ctx, "data/acl/commands.csv")

        delta = int((datetime.now() - now).total_seconds())
        await ctx.send(self.text.get("import", "imported", delta=delta))

    @acl.command(name="import")
    async def acl_import(self, ctx):
        """Import settings from attachment"""
        if len(ctx.message.attachments) != 1 or ctx.message.attachments[0].filename != "rules.csv":
            return await ctx.send(self.text.get("import", "wrong_file"))

        now = datetime.now()
        filename = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ctx.author.id}.csv"

        m = await ctx.send(self.text.get("import", "saving"))
        await ctx.message.attachments[0].save(filename)
        await m.edit(content=self.text.get("import", "importing"))

        await self.import_csv(ctx, filename)

        delta = int((datetime.now() - now).total_seconds())
        await m.edit(content=self.text.get("import", "imported", delta=delta))

    @acl.command(name="export")
    async def acl_export(self, ctx):
        """Export settings to attachment"""
        now = datetime.now()
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ctx.author.id}.csv"

        m = await ctx.send(self.text.get("export", "exporting", filename=filename))
        rules = sorted(repo_a.getRules(), key=lambda rule: rule.command)

        with ctx.typing():
            with open("data/acl/" + filename, "w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["command", "default", "allow", "deny"])
                writer.writeheader()
                for rule in rules:
                    writer.writerow(
                        {
                            "command": rule.command,
                            "default": "1" if rule.default else "0",
                            "allow": " ".join(g.group.name for g in rule.groups if g.allow),
                            "deny": " ".join(g.group.name for g in rule.groups if not g.allow),
                        }
                    )

        delta = int((datetime.now() - now).total_seconds())
        await m.edit(content=self.text.get("export", "exported", delta=delta))
        await ctx.send(file=discord.File(fp="data/acl/" + filename))
        os.remove("data/acl/" + filename)

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

    def get_group_representation(self, guild: discord.Guild, group: ACL_group) -> str:
        """Convert ACL_group object to human-friendly string"""
        template = "Group **{gname}** (id `{gid}`)"

        template_map = "mapped to Discord role **{dname}**"
        if group.parent_id != 0:
            if guild is not None:
                dname = getattr(guild.get_role(group.role_id), "name", "")
            else:
                dname = f"`{group.role_id}`"
        else:
            dname = ""

        template_parent = "has parent group **{pname}** (id `{pid}`)"
        pname = getattr(repo_a.getGroup(group.parent_id), "name", "")

        message = [self.text.get("group_repr", "name", gname=group.name, gid=group.id)]
        if len(dname):
            message.append(self.text.get("group_repr", "map", dname=self.sanitise(dname), did=group.role_id))
        if len(pname):
            message.append(self.text.get("group_repr", "parent", pname=pname, pid=group.parent_id))

        return " ".join(message) + "."

    def get_rule_representation(self, rule: ACL_rule) -> str:
        """Convert ACL_rule object to human-friendly string"""

        template_override = "{}#{}"

        def get_user(discord_id: int) -> str:
            user = self.bot.get_user(discord_id)
            if hasattr(user, "display_name"):
                return user.display_name
            return str(discord_id)

        result = [
            "{default} {command}".format(
                command=rule.command,
                default="+" if rule.default else "-",
            )
        ]

        gallow = " ".join(
            template_override.format(group.group.name, group.id) for group in rule.groups if group.allow
        )
        gdeny = " ".join(
            template_override.format(group.group.name, group.id) for group in rule.groups if not group.allow
        )
        uallow = " ".join(
            template_override.format(get_user(user.discord_id), user.id) for user in rule.users if user.allow
        )
        udeny = " ".join(
            template_override.format(get_user(user.discord_id), user.id)
            for user in rule.users
            if not user.allow
        )

        if len(gallow) or len(uallow):
            result.append(f"  + {' '.join((gallow, uallow))}")
        if len(gdeny) or len(udeny):
            result.append(f"  - {' '.join((gdeny, udeny))}")

        return "\n".join(result)

    async def import_csv(self, ctx: commands.Context, path: str) -> bool:
        """Import rule csv"""
        all_commands = self.get_command_names()
        acl_groups = [g.name for g in repo_a.getGroups()]

        skipped = []
        errors = {}
        done = []

        with open(path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for i, rule in enumerate(reader, 1):
                print(rule)
                # detect misconfigured rows
                if len(rule) != 4:
                    skipped.append(f"{i:>3} | wrong line    | {rule['command']}")
                    continue
                # detect misconfigured commands
                if rule["command"] not in all_commands:
                    skipped.append(f"{i:>3} | no command    | {rule['command']}")
                    continue
                # detect misconfigured defaults
                if rule["default"] not in ("0", "1"):
                    skipped.append(f"{i:>3} | wrong default | {rule['command']}: {rule['default']}")
                    continue
                # detect misconfigured groups
                groups_allowed = [g for g in rule["allow"].split(" ") if len(g)]
                groups_denied = [g for g in rule["deny"].split(" ") if len(g)]
                skip = False
                for group in groups_allowed + groups_denied:
                    if group not in acl_groups:
                        skipped.append(f"{i:>3} | wrong group   | {rule['command']}: {group}")
                        skip = True
                        break
                if skip:
                    continue

                try:
                    repo_a.addRule(command=rule["command"], allow=(rule["default"] == 1))
                    for group in groups_allowed:
                        repo_a.addGroupConstraint(
                            command=rule["command"],
                            identifier=group,
                            allow=True,
                        )
                    for group in groups_denied:
                        repo_a.addGroupConstraint(
                            command=rule["command"],
                            identifier=group,
                            allow=False,
                        )
                    done.append(rule["command"])
                except acl_repo.Duplicate:
                    skipped.append(f"{i:>3} | already set   | {rule['command']}")
                except acl_repo.ACLException as e:
                    errors[rule["command"]] = str(e)

        if len(done):
            await ctx.send(self.text.get("csv_output", "new"))
            await ctx.send("```" + ", ".join(done) + "```")
        if len(skipped):
            await ctx.send(self.text.get("csv_output", "skipped"))
            for page in utils.paginate(skipped):
                await ctx.send("```" + page + "```")
        if len(errors):
            await ctx.send(self.text.get("csv_output", "errors"))
            output = []
            for command, error in errors.items():
                output.append(f"{command}: {error}")
            for page in utils.paginate(output):
                await ctx.send("```" + page + "```")
