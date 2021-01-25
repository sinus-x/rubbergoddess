import json
import os
import re
import tempfile
from datetime import datetime
from typing import List, Optional, Tuple

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

        def bfs(queue) -> list:
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
    @acl_group.command(name="get", aliases=["info"])
    async def acl_group_get(self, ctx, name: str):
        """Get ACL group"""
        result = repo_a.get_group(ctx.guild.id, name)
        if result is None:
            return await ctx.send(self.text.get("group_get", "nothing"))

        await ctx.send(embed=self.get_group_embed(ctx, result))

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
        await ctx.send(embed=self.get_group_embed(ctx, result))
        await self.event.sudo(ctx, f"ACL group added: **{result.name}**.")

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

        await ctx.send(embed=self.get_group_embed(ctx, result))
        await self.event.sudo(ctx, f"ACL group **{result.name}** updated: **{param}={value}**.")

    @commands.check(acl.check)
    @acl_group.command(name="remove", aliases=["delete", "r", "d"])
    async def acl_group_remove(self, ctx, name: str):
        """Remove ACL group"""
        result = repo_a.delete_group(ctx.guild.id, name)
        await ctx.send(embed=self.get_group_embed(ctx, result))
        await self.event.sudo(
            ctx, f"ACL group removed: **{result.get('name')}** (#{result.get('id')})."
        )

    ## Rules

    @commands.guild_only()
    @commands.check(acl.check)
    @acl_.group(name="rule")
    async def acl_rule(self, ctx):
        """Command control"""
        await utils.send_help(ctx)

    @commands.guild_only()
    @commands.check(acl.check)
    @acl_rule.command(name="get", aliases=["info"])
    async def acl_rule_get(self, ctx, command: str):
        """See command's policy"""
        rule = repo_a.get_rule(ctx.guild.id, command)
        if rule is None:
            return await ctx.send(self.text.get("rule_get", "nothing"))

        embed = self.get_rule_embed(ctx, rule)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.check(acl.check)
    @acl_rule.command(name="import")
    async def acl_rule_import(self, ctx, mode: str):
        """Import command rules

        mode: `append` or `replace`
        """
        if len(ctx.message.attachments) != 1:
            return await ctx.send(self.text.get("import", "wrong_file"))
        if not ctx.message.attachments[0].filename.endswith("json"):
            return await ctx.send(self.text.get("import", "wrong_json"))

        if mode not in ("append", "replace"):
            return await ctx.send(self.text.get("import", "wrong_mode"))

        # Download
        data_file = tempfile.TemporaryFile()
        await ctx.message.attachments[0].save(data_file)
        data_file.seek(0)
        try:
            data = json.load(data_file)
        except json.decoder.JSONDecodeError as exc:
            await ctx.send(self.text.get("import", "wrong_json") + f"\n> `{str(exc)}`")

        new, edited, rejected = await self._import_json(ctx, data, mode=mode)
        await ctx.send(self.text.get("import", "imported", new=len(new), edited=len(edited)))

        result = ""
        for (msg, command, reason) in rejected:
            result += "\n> " + self.text.get("import", msg, command=command, reason=reason)
            if len(result) > 1900:
                await ctx.send(result)
                result = ""
        if len(result):
            await ctx.send(result)

        data_file.close()
        await self.event.sudo(ctx, f"Added {len(new)} and edited {len(edited)} ACL rules.")

    @commands.guild_only()
    @commands.check(acl.check)
    @acl_rule.command(name="export")
    async def acl_rule_export(self, ctx):
        """Export command rules"""
        filename = f"acl_{ctx.guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        rules = repo_a.get_rules(ctx.guild.id)
        export = dict()

        for rule in rules:
            export[rule.command] = {
                "default": rule.default,
                "group allow": [g.group.name for g in rule.groups if g.allow],
                "group deny": [g.group.name for g in rule.groups if not g.allow],
                "user allow": [u.user_id for u in rule.users if u.allow],
                "user deny": [u.user_id for u in rule.users if not u.allow],
            }

        file = tempfile.TemporaryFile(mode="w+")
        json.dump(export, file, indent="\t", sort_keys=True)
        file.seek(0)

        await ctx.send(file=discord.File(fp=file, filename=filename))
        file.close()
        await self.event.sudo(ctx, "ACL rules exported.")

    @commands.check(acl.check)
    @acl_rule.command(name="flush", ignore_extra=False)
    async def acl_rule_flush(self, ctx):
        """Flush all the command rules."""
        count = repo_a.delete_rules(ctx.guild.id)
        await ctx.send(self.text.get("rule_flush", count=count))
        await self.event.sudo(ctx, "ACL rules flushed.")

    ##
    ## Logic
    ##

    def get_rule_embed(self, ctx, rule: ACL_rule) -> discord.Embed:
        embed = discord.Embed(
            ctx=ctx,
            title=self.text.get("rule_get", "title", command=rule.command),
        )
        embed.add_field(
            name=self.text.get("rule_get", "default"),
            value=str(rule.default),
            inline=False,
        )
        if len([g for g in rule.groups if g.allow is True]):
            embed.add_field(
                name=self.text.get("rule_get", "group_allow"),
                value=", ".join([g.group.name for g in rule.groups if g.allow is True]),
            )
        if len([g for g in rule.groups if g.allow is False]):
            embed.add_field(
                name=self.text.get("rule_get", "group_deny"),
                value=", ".join([g.group.name for g in rule.groups if g.allow is False]),
            )
        if len([u for u in rule.users if u.allow is True]):
            embed.add_field(
                name=self.text.get("rule_get", "user_allow"),
                value=", ".join(
                    [
                        (self.bot.get_user(u.user_id) or str(u.user_id))
                        for u in rule.users
                        if u.allow is True
                    ],
                ),
            )
        if len([u for u in rule.users if u.allow is False]):
            embed.add_field(
                name=self.text.get("rule_get", "user_deny"),
                value=", ".join(
                    [
                        (self.bot.get_user(u.user_id) or str(u.user_id))
                        for u in rule.users
                        if u.allow is False
                    ]
                ),
            )

        return embed

    def get_group_embed(
        self, ctx: commands.Context, group: Tuple[ACL_group, dict]
    ) -> discord.Embed:
        if type(group) == ACL_group:
            group = group.mirror()

        role = ctx.guild.get_role(group["role_id"])

        embed = discord.Embed(
            ctx=ctx,
            title=self.text.get("group_get", "title", name=group["name"]),
        )
        if role is not None:
            embed.add_field(
                name=self.text.get("group_get", "discord"),
                value=f"{role.name} ({role.id})",
                inline=False,
            )
        if group["parent"] is not None:
            embed.add_field(
                name=self.text.get("group_get", "parent"),
                value=group["parent"],
                inline=False,
            )

        return embed

    async def _import_json(
        self, ctx: commands.Context, data: dict, mode: str
    ) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
        """Import JSON rules

        Returns
        -------
        list: New commands
        list: Altered commands
        list: Rejected commands as (skip/warn, command, reason) tuple
        """
        result_new = list()
        result_alt = list()
        result_rej = list()

        # check data
        for command, attributes in data.items():
            # CHECK
            bad: bool = False

            # bool
            if "default" in attributes:
                if attributes["default"] not in (True, False):
                    result_rej.append(
                        (
                            "skip",
                            command,
                            self.text.get("import", "bad_bool", key="default"),
                        )
                    )
                    bad = True
            else:
                attributes["default"] = False

            if "direct" in attributes:
                if attributes["direct"] not in (True, False):
                    result_rej.append(
                        (
                            "skip",
                            command,
                            self.text.get("import", "bad_bool", key="direct"),
                        )
                    )
                    bad = True
            else:
                attributes["direct"] = False

            # lists
            for keyword in ("group allow", "group deny", "user allow", "user deny"):
                if keyword in attributes:
                    if type(attributes[keyword]) != list:
                        result_rej.append(
                            (
                                "skip",
                                command,
                                self.text.get("import", "bad_list", key=keyword),
                            )
                        )
                        bad = True
                else:
                    attributes[keyword] = list()

            # groups
            for keyword in ("group allow", "group deny"):
                for group in attributes[keyword]:
                    if type(group) != str:
                        result_rej.append(
                            (
                                "skip",
                                command,
                                self.text.get("import", "bad_text", key=group),
                            )
                        )
                        bad = True

            # users
            for keyword in ("user allow", "user deny"):
                for user in attributes[keyword]:
                    if type(user) != int:
                        result_rej.append(
                            (
                                "skip",
                                command,
                                self.text.get("import", "bad_int", key=user),
                            )
                        )
                        bad = True

            if bad:
                # do not proceed to adding
                continue

            # ADD
            try:
                repo_a.add_rule(ctx.guild.id, command, attributes["default"])
                result_new.append(command)
            except acl_repo.Duplicate:
                if mode == "replace":
                    repo_a.delete_rule(ctx.guild.id, command)
                    repo_a.add_rule(ctx.guild.id, command, attributes["default"])
                    result_alt.append(command)
                else:
                    result_rej.append((command, self.text.get("import", "duplicate")))
                    continue

            for group in attributes["group allow"]:
                try:
                    repo_a.add_group_constraint(ctx.guild.id, command, group, allow=True)
                except acl_repo.NotFound:
                    result_rej.append(
                        (
                            "warn",
                            command,
                            self.text.get(
                                "import",
                                "no_group",
                                name=group,
                            ),
                        )
                    )
            for group in attributes["group deny"]:
                try:
                    repo_a.add_group_constraint(ctx.guild.id, command, group, allow=False)
                except acl_repo.NotFound:
                    result_rej.append(
                        (
                            "warn",
                            command,
                            self.text.get(
                                "import",
                                "no_group",
                                name=group,
                            ),
                        )
                    )
            for user in attributes["user allow"]:
                repo_a.add_user_constraint(ctx.guild.id, command, user, allow=True)
            for user in attributes["user deny"]:
                repo_a.add_user_constraint(ctx.guild.id, command, user, allow=False)

        return result_new, result_alt, result_rej
