from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def allow(ctx: commands.Context) -> bool:
    if ctx.author.id == config.author_id:
        return True

    allowed = {"user": False, "channel": False, "group": False}

    # TODO Take into account DMs

    acl_command = repo.getCommand(ctx.qualified_name)  # ??? Is it qualified name ??
    user_groups = [
        group
        for group in [repo.getGroupByRole(role.id) for role in ctx.author.roles]
        if group is not None
    ]
