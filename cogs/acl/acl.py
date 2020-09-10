import csv
import os
import re
from typing import List, Optional
from datetime import datetime

import discord
from discord.ext import commands

from core import acl, rubbercog, utils
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

    @commands.guild_only()
    @commands.check(acl.check)
    @commands.group(name="acl")
    async def acl_(self, ctx):
        """Permission control"""
        await utils.send_help(ctx)

    ## Groups

    @commands.check(acl.check)
    @acl_.group(name="group", aliases=["g"])
    async def acl_group(self, ctx):
        """ACL group control"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @acl_group.command(name="list", aliases=["l"])
    async def acl_group_list(self, ctx):
        """List ACL groups"""
        groups = repo_a.get_groups(ctx.guild.id)

        if not len(groups):
            return await ctx.send(self.text.get("group_list", "nothing"))

        # compute relationships between groups
        relationships = {}
        for group in groups:
            if group.name not in relationships:
                relationships[group.name] = []
            if group.parent is not None:
                # add to parent's list
                if group.parent not in relationships:
                    relationships[group.parent] = []
                relationships[group.parent].append(group)

        # add relationships to group objects
        for group in groups:
            group.children = relationships[group.name]
            group.level = 0

        def bfs(queue):
            visited = []
            while queue:
                group = queue.pop(0)
                if group not in visited:
                    visited.append(group)
                    # build levels for intendation
                    for child in group.children:
                        child.level = group.level + 1
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

    @commands.check(acl.check)
    @acl_group.command(name="get", aliases=["g"])
    async def acl_group_get(self, ctx, name: str):
        """Get ACL group"""
        result = repo_a.get_group(ctx.guild.id, name)

        if result is None:
            return await ctx.send(self.text.get("group_get", "nothing"))

        await ctx.send(self.get_group_representation(ctx.guild, result))

    @commands.check(acl.check)
    @acl_group.command(name="add", aliases=["a"])
    async def acl_group_add(self, ctx, name: str, parent: str, role_id: int):
        """Add ACL group

        name: string matching `[a-zA-Z-]+`
        parent: parent group name
        role_id: Discord role ID

        To unlink the group from any parents, set parent to "".
        To set up virtual group with no link to discord roles, set role_id to 0.
        """
        regex = r"[a-zA-Z-]+"
        if re.fullmatch(regex, name) is None:
            return await ctx.send(self.text.get("group_regex", regex=regex))

        if len(parent) == 0:
            parent = None
        result = repo_a.add_group(ctx.guild.id, name, parent, role_id)
        await ctx.send(self.get_group_representation(ctx.guild, result))
        await self.event.sudo(ctx, f"ACL group added: **{result.name}** (#{result.id}).")

    @commands.check(acl.check)
    @acl_group.command(name="edit", aliases=["e"])
    async def acl_group_edit(self, ctx, name: str, param: str, value):
        """Edit ACL group

        name: string matching `[a-zA-Z-]+`

        Options:
        name, string matching `[a-zA-Z-]+`
        parent, parent group name
        role_id, Discord role ID

        To unlink the group from any parents, set parent to "".
        To set up virtual group with no link to discord roles, set role_id to 0.
        """
        if param == "name":
            regex = r"[a-zA-Z-]+"
            if re.fullmatch(regex, value) is None:
                return await ctx.send(self.text.get("group_regex", regex=regex))
            result = repo_a.edit_group(ctx.guild.id, name=name, new_name=value)
        elif param == "parent":
            result = repo_a.edit_group(ctx.guild.id, name=name, parent=value)
        elif param == "role_id":
            result = repo_a.edit_group(ctx.guild.id, name=name, role_id=int(value))
        else:
            raise discord.BadArgument()

        await ctx.send(self.get_group_representation(ctx.guild, result))
        await self.event.sudo(ctx, f"ACL group **{result.name}** updated: **{param}={value}**.")

    @commands.check(acl.check)
    @acl_group.command(name="remove", aliases=["delete", "r", "d"])
    async def acl_group_remove(self, ctx, name: str):
        """Remove ACL group"""
        result = repo_a.delete_group(ctx.guild.id, name)
        await ctx.send(self.get_group_mirror_representation(ctx.guild, result))
        await self.event.sudo(
            ctx, f"ACL group removed: **{result.get('name')}** (#{result.get('id')})."
        )

    ## Rules

    @commands.check(acl.check)
    @acl_.group(name="rule")
    async def acl_rule(self, ctx):
        """Command control"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @acl_rule.command(name="get")
    async def acl_rule_get(self, ctx, command: str):
        """See command's policy"""
        rule = repo_a.get_rule(ctx.guild.id, command)
        if rule is None:
            return await ctx.send(self.text.get("rule_get", "nothing"))

        await ctx.send("```\n" + self.get_rule_representation(rule) + "```")

    @commands.check(acl.check)
    @acl_rule.command(name="add")
    async def acl_rule_add(self, ctx, command: str, default: bool = False):
        """Add command"""
        if command not in self.get_command_names():
            return await ctx.send(self.text.get("rule_add", "nothing"))
        result = repo_a.add_rule(ctx.guild.id, command)
        await ctx.send("```" + self.get_rule_representation(result) + "```")
        await self.event.sudo(ctx, f"ACL rule added: **{result.command}** (#{result.id}).")

    @commands.check(acl.check)
    @acl_rule.command(name="remove", aliases=["delete"])
    async def acl_rule_remove(self, ctx, command: str):
        """Remove command"""
        result = repo_a.delete_rule(ctx.guild.id, command)
        await ctx.send("```" + self.get_rule_mirror_representation(result) + "```")
        await self.event.sudo(
            ctx, f"ACL rule removed: **{result.get('command')}** (#{result.get('id')})."
        )

    @commands.check(acl.check)
    @acl_rule.command(name="flush")
    async def acl_rule_flush(self, ctx):
        """Remove all commands"""
        result = repo_a.delete_rules(ctx.guild.id)
        await ctx.send(self.text.get("rule_flush", count=result))
        await self.event.sudo(ctx, "ACL rules flushed.")

    ## Constraints

    @commands.check(acl.check)
    @acl_rule.command(name="default")
    async def acl_rule_default(self, ctx, command: str, allow: bool):
        """Set default response"""
        result = repo_a.edit_rule(ctx.guild.id, command, allow)
        await ctx.send("```" + self.get_rule_representation(result) + "```")
        await self.event.sudo(ctx, f"ACL rule default for **{result.command}** set to **{allow}**.")

    @commands.check(acl.check)
    @acl_.group(name="user_constraint", aliases=["constraint_user", "uc"])
    async def acl_user_constraint(self, ctx):
        """Manage command constraints"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @acl_user_constraint.command(name="add", aliases=["a"])
    async def acl_user_constraint_add(self, ctx, command: str, user_id: int, allow: bool):
        """Add command constraint

        command: A command
        user_id: User ID
        allow: True or False
        """
        result = repo_a.add_user_constraint(ctx.guild.id, user_id, command, allow)
        await ctx.send("```" + self.get_rule_representation(result) + "```")
        await self.event.sudo(
            ctx, f"ACL user constraint for **{result.command}** added: **{user_id}={allow}**."
        )

    @commands.check(acl.check)
    @acl_user_constraint.command(name="remove", aliases=["r"])
    async def acl_user_constraint_remove(self, ctx, constraint_id: int):
        """Remove command constraint

        constraint_id: User constraint ID
        """
        result = repo_a.remove_user_constraint(constraint_id)
        await ctx.send(
            self.text.get("user_constraint", "removed")
            if result
            else self.text.get("user_constraint", "nothing")
        )
        await self.event.sudo(ctx, f"ACL user constraint **#{constraint_id}** removed.")

    @commands.check(acl.check)
    @acl_.group(name="group_constraint", aliases=["constraint_group", "gc"])
    async def acl_group_constraint(self, ctx):
        """Manage group command constraints"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @acl_group_constraint.command(name="add", aliases=["a"])
    async def acl_group_constraint_add(self, ctx, command: str, group: str, allow: str):
        """Add command constraint

        command: A command
        group: ACL group name or ID
        allow: boolean
        """
        allow = allow in ("True", "true", "1")

        result = repo_a.add_group_constraint(ctx.guild.id, group, command, allow)
        await ctx.send("```" + self.get_rule_representation(result) + "```")
        await self.event.sudo(
            ctx, f"ACL group constraint for **{result.command}** added: **{group}={allow}**."
        )

    @commands.check(acl.check)
    @acl_group_constraint.command(name="remove", aliases=["r"])
    async def acl_group_constraint_remove(self, ctx, constraint_id: int):
        """Remove command constraint

        command: A command
        constraint_id: Group constraint ID
        """
        result = repo_a.remove_group_constraint(constraint_id)
        await ctx.send(
            self.text.get("group_constraint", "removed")
            if result
            else self.text.get("group_constraint", "nothing")
        )
        await self.event.sudo(ctx, f"ACL group constraint **#{constraint_id}** removed.")

    ## Security

    @commands.check(acl.check)
    @acl_.command(name="audit")
    async def acl_audit(self, ctx, search: str = None):
        """Make security audit

        search: Only display commands containing the `search` string
        """
        rules = repo_a.get_rules(ctx.guild.id)
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

    @commands.check(acl.check)
    @acl_.command(name="check")
    async def acl_check(self, ctx):
        """Check, if all commands are in database"""
        commands = self.get_free_commands(ctx.guild.id)
        output = utils.paginate(commands)
        for page in output:
            if len(page):
                await ctx.send("```" + page + "```")
        if len(commands):
            await ctx.send(self.text.get("check", "some", count=len(commands)))
        else:
            await ctx.send(self.text.get("check", "none"))

    ## Import & Export

    @commands.check(acl.check)
    @acl_.command(name="init")
    async def acl_init(self, ctx):
        """Load default settings from file"""
        now = datetime.now()

        await self.import_csv(ctx, "data/acl/rules.csv")

        delta = int((datetime.now() - now).total_seconds())
        await ctx.send(self.text.get("import", "imported", delta=delta))
        await self.event.sudo(ctx, "ACL rules initiated.")

    @commands.check(acl.check)
    @acl_.command(name="import")
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
        await self.event.sudo(ctx, "ACL rules imported.")

    @commands.check(acl.check)
    @acl_.command(name="export")
    async def acl_export(self, ctx):
        """Export settings to attachment"""
        now = datetime.now()
        filename = f"export_{ctx.guild.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        m = await ctx.send(self.text.get("export", "exporting", filename=filename))
        rules = sorted(repo_a.get_rules(), key=lambda rule: rule.command)

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
        await ctx.send(ctx, "ACL rules exported.")

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
        self, guild_id: int, *, commands: List[str] = None, rules: List[ACL_rule] = None
    ) -> Optional[List[str]]:
        """Return list of commands not in database"""
        if commands is None:
            commands = self.get_command_names()
        if rules is None:
            rules = repo_a.get_rules(guild_id)

        for rule in rules:
            if rule.command in commands:
                commands.remove(rule.command)
        return commands

    def get_group_representation(self, guild: discord.Guild, group: ACL_group) -> str:
        """Convert ACL_group object to human-friendly string"""
        group_role = getattr(guild.get_role(group.role_id), "name", "")

        message = [self.text.get("group_repr", "name", name=group.name)]
        if len(group_role):
            message.append(
                self.text.get(
                    "group_repr", "map", dname=self.sanitise(group_role), did=group.role_id
                )
            )
        if group.parent is not None:
            message.append(self.text.get("group_repr", "parent", parent=group.parent))

        return " ".join(message) + "."

    def get_group_mirror_representation(self, guild: discord.Guild, mirror: dict) -> str:
        """Convert dictionary to human-friendly string"""
        group_role = getattr(guild.get_role(mirror.get("role_id")), "name", "")

        message = [self.text.get("group_repr", "name", name=mirror.get("name"))]
        if len(group_role):
            message.append(
                self.text.get(
                    "group_repr", "map", dname=self.sanitise(group_role), did=mirror.get("role_id")
                )
            )
        if mirror.get("parent") is not None:
            message.append(self.text.get("group_repr", "parent", parent=mirror.get("parent")))

        return " ".join(message) + "."

    def get_rule_representation(self, rule: ACL_rule) -> str:
        """Convert ACL_rule object to human-friendly string"""
        template = "{}#{}"

        def get_user(user_id: int) -> str:
            return getattr(self.bot.get_user(user_id), "display_name", str(user_id))

        result = [
            "{default} {command}".format(
                command=rule.command,
                default="+" if rule.default else "-",
            )
        ]

        gallow = " ".join(
            template.format(group.group.name, group.id) for group in rule.groups if group.allow
        )
        gdeny = " ".join(
            template.format(group.group.name, group.id) for group in rule.groups if not group.allow
        )
        uallow = " ".join(
            template.format(get_user(user.user_id), user.id) for user in rule.users if user.allow
        )
        udeny = " ".join(
            template.format(get_user(user.user_id), user.id)
            for user in rule.users
            if not user.allow
        )

        if len(gallow) or len(uallow):
            result.append(f"  + {' '.join((gallow, uallow))}")
        if len(gdeny) or len(udeny):
            result.append(f"  - {' '.join((gdeny, udeny))}")

        return "\n".join(result)

    def get_rule_mirror_representation(self, mirror: dict) -> str:
        """Convert dictionary to human-friendly string"""
        template = "{}#{}"

        def get_user(user_id: int) -> str:
            return getattr(self.bot.get_user(user_id), "display_name", str(user_id))

        result = [
            "{default} {command}".format(
                command=mirror.get("command"),
                default="+" if mirror.get("default") else "-",
            )
        ]

        gallow = " ".join(
            template.format(group.get("name"), group.get("id"))
            for group in mirror.get("groups")
            if group.get("allow")
        )
        gdeny = " ".join(
            template.format(group.get("name"), group.get("id"))
            for group in mirror.get("groups")
            if not group.get("allow")
        )
        uallow = " ".join(
            template.format(get_user(user.get("user_id")), user.get("id"))
            for user in mirror.get("users")
            if user.get("allow")
        )
        udeny = " ".join(
            template.format(get_user(user.get("user_id")), user.get("id"))
            for user in mirror.get("users")
            if not user.get("allow")
        )

        if len(gallow) or len(uallow):
            result.append(f"  + {' '.join((gallow, uallow))}")
        if len(gdeny) or len(udeny):
            result.append(f"  - {' '.join((gdeny, udeny))}")

        return "\n".join(result)

    async def import_csv(self, ctx: commands.Context, path: str) -> bool:
        """Import rule csv"""
        all_commands = self.get_command_names()
        acl_groups = [g.name for g in repo_a.get_groups(ctx.guild.id)]

        skipped = []
        errors = {}
        done = []

        with open(path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for i, rule in enumerate(reader, 1):
                # skip comments
                if rule["command"].startswith("#"):
                    continue
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
                    repo_a.add_rule(ctx.guild.id, rule["command"], (rule["default"] == 1))
                    for group in groups_allowed:
                        repo_a.add_group_constraint(
                            guild_id=ctx.guild.id,
                            name=group,
                            command=rule["command"],
                            allow=True,
                        )
                    for group in groups_denied:
                        repo_a.add_group_constraint(
                            guild_id=ctx.guild.id,
                            name=group,
                            command=rule["command"],
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
