from discord.ext import commands

from core.config import config
from repository import acl_repo

repo = acl_repo.ACLRepository()


def check(ctx: commands.Context) -> bool:
    if ctx.author.id == config.author_id:
        return True

    # TODO Take into account DMs
    # FIXME What to do if the command is not found?

    acl_command = repo.getCommand(ctx.qualified_name)
    user_role_ids = [role.id for role in ctx.author.roles]

    ##
    ## Initiate variables
    ##

    # The default is blocking: only deny where allow is False.
    # If there is just one entry with allow set to True, only those will be accepted.
    allow_channel = False
    channels_strict = False
    allow_group = False
    groups_strict = False

    allow_user = False

    ##
    ## Resolve
    ##

    # get channel information
    for channel in acl_command.channels:
        if ctx.channel.id == channel.item_id and channel.allow == False:
            return False

        if channel.allow == True:
            channels_strict = True

        if ctx.channel.id == channel.item_id and channel.allow == True:
            allow_channel = True

    if channels_strict and not allow_channel:
        return False

    # get user information
    for user in acl_command.users:
        if ctx.author.id == user.item_id and user.allow == False:
            return False

        if ctx.author.id == user.item_id and user.allow == True:
            allow_user = True
            break

    # get group information
    for group in acl_command.groups:
        # do not return False if group.allow is False, there can be user override

        if group.allow == True:
            groups_strict = True

        if group.item_id in user_role_ids and group.allow == True:
            allow_group = True

    if groups_strict and not allow_group and not allow_user:
        return False

    # we do not need to check channel, it has been filtered
    return allow_user or allow_group
