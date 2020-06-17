import discord
from discord.ext import commands

from core.config import config
from core.text import text


def is_bot_owner(ctx: commands.Context):
    return ctx.author.id == config.admin_id


def is_mod(ctx: commands.Context):
    for role in __getAuthor(ctx).roles:
        if role.id == config.role_mod:
            return True
    return False


def is_elevated(ctx: commands.Context):
    for role in __getAuthor(ctx).roles:
        if role.id in config.roles_elevated:
            return True
    return False


def is_native(ctx: commands.Context):
    for role in __getAuthor(ctx).roles:
        if role.id in config.roles_native:
            return True
    return False


def is_verified(ctx: commands.Context):
    for role in __getAuthor(ctx).roles:
        if role.id == config.role_verify:
            return True
    return False


def is_quarantined(ctx: commands.Context):
    for role in __getAuthor(ctx).roles:
        if role.id == config.get("roles", "quarantine_id"):
            return True
    return False


def is_not_verified(ctx: commands.Context):
    return not is_verified(ctx) or is_quarantined(ctx)


def is_in_modroom(ctx: commands.Context):
    return ctx.channel.id == config.channel_mods


def is_in_botroom(ctx: commands.Context):
    return ctx.channel.id in config.bot_allowed


def is_in_jail(ctx: commands.Context):
    return ctx.channel.id == config.get("channels", "jail")


def is_in_jail_or_dm(ctx: commands.Context):
    return ctx.channel.id == config.get("channels", "jail") or isinstance(
        ctx.message.channel, discord.DMChannel
    )


def is_in_quarantine(ctx):
    return ctx.channel.id == config.get("channels", "quarantine")


def is_in_quarantine_or_dm(ctx):
    return ctx.channel.id == config.get("channels", "quarantine") or isinstance(
        ctx.message.channel, discord.DMChannel
    )


def is_in_voice(ctx: commands.Context):
    return (
        ctx.channel.id == config.channel_nomic
        and ctx.author.voice is not None
        and ctx.author.voice.channel is not None
    )


def __getAuthor(ctx: commands.Context):
    u = ctx.bot.get_guild(config.guild_id).get_member(ctx.author.id)
    if u is not None:
        return u
    raise commands.CommandError("Not in master guild.")


async def antispam(ctx: commands.Context):
    """Send botroom redirect if needed"""
    if not isinstance(ctx.channel, discord.TextChannel):
        return

    if ctx.channel.id in config.get("channels", "bot allowed"):
        return

    await ctx.send(
        text.fill("server", "botroom redirect"),
        user=ctx.author,
        channel=config.get("channels", "botspam"),
    )
