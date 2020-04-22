import discord
from discord.ext import commands

from config.config import config

 
def is_bot_owner(ctx: commands.Context):
    return ctx.author.id == config.admin_id

def is_mod(ctx: commands.Context):
    for role in ctx.author.roles:
        if role.id == config.role_mod:
            return True
    return False

def is_elevated(ctx: commands.Context):
    for role in ctx.author.roles:
        if role.id in config.roles_elevated:
            return True
    return False

def is_native(ctx: commands.Context):
    for role in ctx.author.roles:
        if role.id in config.roles_native:
            return True
    return False

def is_verified(ctx: commands.Context):
    for role in ctx.author.roles:
        if role.id in config.role_verify:
            return True
    return False

def is_not_verified(ctx: commands.Context):
    #TODO Adjust when we have REVERIFY role
    return not is_verified(ctx)


def is_in_modroom(ctx: commands.Context):
    return ctx.channel.id == config.channel_mods

def is_in_botroom(ctx: commands.Context):
    return ctx.channel.id in config.bot_allowed

def is_in_jail(ctx: commands.Context):
    return ctx.channel.id == config.channel_jail

def is_in_jail_or_dm(ctx: commands.Context):
    return ctx.channel.id == config.channel_jail \
    or isinstance(ctx.message.channel, discord.DMChannel)

def is_in_voice(ctx: commands.Context):
    return ctx.channel.category_id == config.channel_voice \
    and ctx.author.voice.channel is not None