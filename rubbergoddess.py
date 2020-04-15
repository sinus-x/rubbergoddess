import traceback

from discord.ext import commands

import utils
from config.config import Config as config
from features import presence
from repository.database import database, session
from repository.user_repo import UserRepository
from repository.review_repo import ReviewRepository

import discord
from datetime import datetime

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*config.prefixes),
                   help_command=None, case_insensitive=True)

presence = presence.Presence(bot)


# fill DB with subjects shortcut, needed for reviews
def load_subjects():
    review_repo = ReviewRepository()
    for subject in config.subjects:
        review_repo.add_subject(subject)


@bot.event
async def on_ready():
    """If Rubbergoddess is ready"""
    print("Ready")
    channel = bot.get_channel(config.channel_log)

    await presence.set_presence()


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(config.channel_botdev)
    output = traceback.format_exc()
    print(output)
    if channel is not None:
        await channel.send("```\n" + output + "\n```")


@bot.command()
async def pull(ctx):
    if ctx.author.id == config.admin_id:
        try:
            utils.git_pull()
            await ctx.send("Git pulled")
        except Exception:
            await ctx.send("Git pull error")
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))


@bot.command()
async def load(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.load_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} loaded')
        except Exception:
            await ctx.send("loading error")
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))


@bot.command()
async def unload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} unloaded')
        except Exception:
            await ctx.send("unloading error")
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))


@bot.command()
async def reload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.reload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} reloaded')
        except Exception:
            await ctx.send("reloading error")
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))


@reload.error
@load.error
@unload.error
async def missing_arg_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Missing argument.')

#database.base.metadata.drop_all(database.db)
database.base.metadata.create_all(database.db)
session.commit()  # Making sure

#load_subjects()

for extension in config.extensions:
    bot.load_extension(f'cogs.{extension}')
    print('{} cog loaded'.format(extension.upper()))

bot.run(config.key)
