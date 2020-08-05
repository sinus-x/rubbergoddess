import discord
from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def check(ctx: commands.Context) -> bool:
    if ctx.author.id == config.admin_id:
        # return True
        pass

    rule = repo.getRule(ctx.command.qualified_name)

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
            group = repo.getGroupByRole(role.id)
            if group is not None:
                break
        else:
            group = repo.getGroup(0)

        # get group hierarchy
        while group:
            for rule_group in rule.groups:
                if rule_group.group == group and rule_group.allow is not None:
                    return rule_group.allow
            group = repo.getGroup(group.parent_id)

    # no settings found, return default
    return rule.default
