from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def allow(ctx: commands.Context) -> bool:
    if ctx.author.id == config.author_id:
        return True

    # TODO Take into account DMs

    acl_command = repo.getCommand(ctx.qualified_name)  # ??? Is it qualified name ???
    user_role_ids = [role.id for role in ctx.author.roles]
    user_groups = [
        group
        for group in [repo.getGroupByRole(role.id) for role in ctx.author.roles]
        if group is not None
    ]

    ##
    ## Initiate variables
    ##

    allow_channel = False
    channels_strict = False
    # The default is channel blocking, eg. specify channels that shouldn't have the command available.
    # If there are channels that have access set to True, only those can be used.

    allow_group = False
    groups_strict = False
    # The default is group blocking, eg. specify groups that shouldn't have access.
    # If there are groups that have access set to True, only those can be used.

    ##
    ## Resolve
    ##

    # get channel information
    for channel in acl_command.channels:
        if channel.item_id == ctx.channel.id and channel.allow == False:
            return False

        if channel.allow == True:
            channels_strict = True

        if channel.item_id == ctx.channel.id and channel.allow == True:
            allow_channel = True

    if channels_strict and allow_channel != True:
        return False

    # get user information
    for user in acl_command.users:
        if user.item_id == ctx.author.id and user.allow == False:
            return False

        if user.item_id == ctx.author.id and user.allow == True:
            break

    # get group information
    for group in acl_command.groups:
        if group.item_id in user_role_ids and group.allow == False:
            return False

        if group.allow == True:
            groups_strict = True

        if group.item_id in user_role_ids and group.allow == True:
            allow_group = True

    if groups_strict and allow_group != True:
        return False

    return allow_channel and allow_group
