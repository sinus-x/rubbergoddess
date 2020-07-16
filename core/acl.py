from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def allow(ctx: commands.Context) -> bool:
    if ctx.author.id == config.author_id:
        return True

    # TODO Take into account DMs

    acl_command = repo.getCommand(ctx.qualified_name)  # ??? Is it qualified name ???
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
    # The default is channel blocking, eg. specify channels that shouldn't have
    # the command available.
    # If there are channels that have access set to True, only those can be used.

    ##
    ## Resolve discord ID-based access
    ##

    # get channel information
    for channel in acl_command.channels:
        if channel.item_id == ctx.channel.id and channel.allow == False:
            return False

        if channel.allow == True:
            channels_strict = True

        if channel.item_id == ctx.channel.id and channel.allow == True:
            allow_channel = True
            break

    if channels_strict and allow_channel != True:
        return False

    # get user information
    for user in acl_command.users:
        if user.item_id == ctx.author.id and user.allow == False:
            return False

        if user.item_id == ctx.author.id and user.allow == True:
            break

    ##
    ## Resolve groups
    ##

    groups = []
    for group in user_groups:
        # check it and check its parents -- if the role is in acl_command.groups, add to list
        pass
