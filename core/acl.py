from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def check(ctx: commands.Context) -> bool:
    if ctx.author.id == config.admin_id:
        return True

    if ctx.guild is None:
        # do not allow invocation in DM
        return False

    rule = repo.get_rule(ctx.guild.id, ctx.command.qualified_name)

    # do not allow execution of unknown functions
    if rule is None:
        return False

    # test for user override
    for user in rule.users:
        if ctx.author.id == user.discord_id:
            return user.allow

    # resolve groups
    if hasattr(ctx.author, "roles"):
        # get user's top role
        for role in ctx.author.roles[::-1]:
            group = repo.get_group_by_role(role.id)
            if group is not None:
                break
        else:
            group = None

        # get group hierarchy
        while group:
            for rule_group in rule.groups:
                if rule_group.group == group and rule_group.allow is not None:
                    return rule_group.allow
            group = repo.get_group(group.guild_id, group.parent)

    # no settings found, return default
    return rule.default
