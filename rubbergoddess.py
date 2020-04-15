import traceback
from datetime import datetime

import discord
from discord.ext import commands

from core import utils, rubbercog
from config.config import config
from config.emotes import Emotes as emote
from features import presence
from repository.database import database
from repository.database import session
from repository.database.karma import Karma, Karma_emoji
from repository.database.review import Review, ReviewRelevance, Subject
from repository.database.verification import User
from repository.review_repo import ReviewRepository

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*config.prefix),
                   help_command=None, case_insensitive=True)

presence = presence.Presence(bot)
rubbercog = rubbercog.Rubbercog(bot)

# fill DB with subjects shortcut, needed for reviews
def load_subjects():
    review_repo = ReviewRepository()
    for subject in config.subjects:
        review_repo.add_subject(subject)


@bot.event
async def on_ready():
    """If Rubbergoddess is ready"""
    print("Logged in.")
    await presence.set_presence()


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(config.channel_botdev)
    output = traceback.format_exc()
    print(output)
    output = list(output[0+i:1960+i] for i in range(0, len(output), 1960))
    if channel is not None:
        for message in output:
            await channel.send("```\n{}```".format(message))


@bot.command()
async def load(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.load_extension(f'cogs.{extension}')
            await ctx.send(f'Rozšíření **{extension}** načteno.')
            await rubbercog.log(ctx, f"Cog {extension} loaded")
        except Exception:
            await ctx.send(f'Načtení rozšíření **{extension}** se nezdařilo.')
            await rubbercog.log(ctx, "Cog loading failed", msg=e)
    else:
        raise commands.NotOwner()


@bot.command()
async def unload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Rozšíření **{extension}** odebráno.')
            await rubbercog.log(ctx, f"Cog {extension} unloaded")
        except Exception:
            await ctx.send(f'Odebrání rozšíření **{extension}** se nezdařilo.')
            await rubbercog.log(ctx, "Cog unloading failed", msg=e)
    else:
        raise commands.NotOwner()


@bot.command()
async def reload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Rozšíření **{extension}** aktualizováno.')
            await rubbercog.log(ctx, f"Cog {extension} reloaded")
        except Exception:
            await ctx.send(f'Aktualizace rozšíření **{extension}** se nepovedla.')
            await rubbercog.log(ctx, "Cog reloading failed", msg=e)
    else:
        raise commands.NotOwner()


@reload.error
@load.error
@unload.error
async def missing_arg_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
       await ctx.send(f'Nesprávný počet argumentů' + emote.sad)

#database.base.metadata.drop_all(database.db)
database.base.metadata.create_all(database.db)
session.commit()  # Making sure

load_subjects()

for extension in config.extensions:
    bot.load_extension(f'cogs.{extension}')
    print('{} extension loaded.'.format(extension.upper()))

bot.run(config.key)
