import git

import discord
from discord.ext import commands

from core.config import config
from core.text import text
from config.messages import Messages


def git_hash():
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha


def git_commit_msg():
    repo = git.Repo(search_parent_directories=True)
    return repo.head.commit.message


def git_pull():
    repo = git.Repo(search_parent_directories=True)
    cmd = repo.git
    return cmd.pull()


def str_emoji_id(emoji):
    if isinstance(emoji, int):
        return str(emoji)

    return emoji if isinstance(emoji, str) else str(emoji.id)


def has_role(user, role):
    if type(user) != discord.Member:
        return None

    try:
        int(role)
        return role in [u.id for u in user.roles]
    except ValueError:
        return role.lower() in [u.name.lower() for u in user.roles]
    return


def fill_message(message_name, *args, **kwargs):
    """Fills message template from messages by attempting to get the attr.
    :param message_name: {str} message template name
    :kwargs: {dict} data for formatting the template
    :return: filled template
    """

    def generate_mention(user_id):
        return "<@" + str(user_id) + ">"

    # Convert username/admin to a mention
    if "user" in kwargs:
        kwargs["user"] = generate_mention(kwargs["user"])

    if "admin" in kwargs:
        kwargs["admin"] = generate_mention(kwargs["admin"])

    # Attempt to get message template and fill
    try:
        template = getattr(Messages, message_name)
        return template.format(*args, **kwargs)
    except AttributeError:
        raise ValueError("Invalid template {}".format(message_name))


def seconds2str(time):
    time = int(time)
    D = 3600 * 24
    H = 3600
    M = 60

    d = (time - (time % D)) / D
    h = (time - (time % H)) / H
    m = (time - (time % M)) / M
    s = time % 60

    if d > 0:
        return f"{d} d, {h:02}:{m:02}:{s:02}"
    if h > 0:
        return f"{h}:{m:02}:{s:02}"
    if m > 0:
        return f"{m}:{s:02}"
    if s > 4:
        return f"{s} vteřin"
    if s > 1:
        return f"{s} vteřiny"
    return "vteřinu"


async def room_check(ctx: commands.Context):
    if not isinstance(ctx.channel, discord.TextChannel):
        return

    if ctx.channel.id not in config.get("channels", "bot allowed"):
        # we do not have `bot` variable, so we have to construct the botroom mention directly
        await ctx.send(
            text.fill(
                "server",
                "botroom redirect",
                mention=ctx.author.mention,
                channel=f"<#{config.get('channels', 'botspam')}>",
            )
        )


async def delete(ctx: commands.Context):
    if hasattr(ctx, "message"):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass


async def send_help(ctx: commands.Context):
    if not hasattr(ctx, "command") or not hasattr(ctx.command, "qualified_name"):
        return
    if ctx.invoked_subcommand is not None:
        return
    await ctx.send_help(ctx.command.qualified_name)
