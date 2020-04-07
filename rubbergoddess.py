import traceback
from datetime import datetime

import discord
from discord.ext import commands

from core import utils
from config.config import config
from config.emotes import Emotes as emote
from features import presence
from repository.database import database
from repository.database import session

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*config.prefix),
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
    print("Jsem přihlášena.")
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
            await ctx.send(f'Stažení aktualizace proběhlo úspěšně.')
        except Exception:
            await ctx.send(f'Při stahování aktualizace došlo k chybě.')
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))
        #TODO log event


@bot.command()
async def load(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.load_extension(f'cogs.{extension}')
            await ctx.send(f'Načetla jsem roli **{extension}**.')
        except Exception:
            await ctx.send(f'Načtení role **{extension}** se nepovedlo.')
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))


@bot.command()
async def unload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Odebrala jsem roli **{extension}**.')
        except Exception:
            await ctx.send(f'Odebrání role **{extension}** se nepovedlo.')
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))
        #TODO log event


@bot.command()
async def reload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Aktualizovala jsem roli **{extension}**.')
        except Exception:
            await ctx.send(f'Aktualizace role **{extension}** se nepovedla.')
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))
        #TODO log event


@reload.error
@load.error
@unload.error
async def missing_arg_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
       await ctx.send(f'Nesprávný počet argumentů' + emote.sad)

#database.base.metadata.drop_all(database.db)
database.base.metadata.create_all(database.db)
session.commit()  # Making sure

#load_subjects()

for extension in config.extensions:
    bot.load_extension(f'cogs.{extension}')
    print('Načetla jsem roli {}.'.format(extension.upper()))

bot.run(config.key)
