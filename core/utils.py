import git
import discord
from discord.ext import commands

from core import config
from config.messages import Messages


def generate_mention(user_id):
    return "<@" + str(user_id) + ">"


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


async def notify(ctx: commands.Context, msg: str):
    """Show an embed.

    A skinny version of rubbercog.throwNotification()
    """
    if ctx.message is None:
        return
    if msg is None:
        msg = ""
    embed = discord.Embed(title=ctx.message.content, color=config.color)
    embed.add_field(name="Výsledek", value=msg, inline=False)
    embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed, delete_after=config.delay_embed)
