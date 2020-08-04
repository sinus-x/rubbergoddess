from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def check(ctx: commands.Context) -> bool:
    if ctx.author.id == config.admin_id:
        # return True
        pass

    # FIXME Take into account DMs
    # FIXME What if the user does not have any role?
    # FIXME What to do if the command is not found?

    rule = repo.getRule(ctx.command.qualified_name)

    # do not allow execution of unknown functions
    if rule is None:
        return False

    # get user's top role
    # FIXME Is this the right way around?
    for role in ctx.author.roles:
        group = repo.getGroupByRole(role.id)
        if group is not None:
            break
    else:
        group = repo.getGroupByRole(0)

    # resolve
    for user in rule.users:
        if ctx.author.id == user.discord_id:
            return user.allow

    while group:
        for rule_group in rule.groups:
            if rule_group.group == group and rule_group.allow is not None:
                return rule_group.allow
        group = repo.getGroup(group.parent_id)

    return False
