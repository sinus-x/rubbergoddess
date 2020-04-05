import traceback
from datetime import datetime

import discord
from discord.ext import commands

from config.config import config
from core import utils
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
    print("Ready")
    channel = bot.get_channel(config.channel_botlog)

    embed = discord.Embed(title="Přihlášení", color=config.color_success)
    embed.add_field(inline=True,
        name="{timestamp}".format(timestamp=datetime.now().
            strftime("%Y-%m-%d %H:%M:%S")),
        value="Commit **{commit}**".format(commit=utils.git_hash()[:7]))
    embed.add_field(inline=True,
        name="Server", value=config.host if config.host else "_unknown_")
    embed.add_field(inline=False,
        name="Povolená rozšíření",
        value=", ".join(config.extensions))
    await channel.send(embed=embed)

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
            await utils.notify(ctx, "Úspěšně dokončeno")
        except Exception:
            await utils.notify(ctx, "Došlo k chybě")
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))
        #TODO log event


@bot.command()
async def load(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.load_extension(f'cogs.{extension}')
            await utils.notify(ctx, f'Přidáno: {extension}')
        except Exception:
            await utils.notify(ctx, "Došlo k chybě")
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))


@bot.command()
async def unload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await utils.notify(ctx, f'Odebráno: {extension}')
        except Exception:
            await utils.notify(ctx, "Došlo k chybě")
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))
        #TODO log event


@bot.command()
async def reload(ctx, extension):
    if ctx.author.id == config.admin_id:
        try:
            bot.unload_extension(f'cogs.{extension}')
            await utils.notify(ctx, f'Restartováno: {extension}')
        except Exception:
            await utils.notify(ctx, "Došlo k chybě")
            #TODO log event
    else:
        await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))
        #TODO log event


@reload.error
@load.error
@unload.error
async def missing_arg_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await utils.notify(ctx, "Nesprávný počet argumentů")

#database.base.metadata.drop_all(database.db)
database.base.metadata.create_all(database.db)
session.commit()  # Making sure

#load_subjects()

for extension in config.extensions:
    bot.load_extension(f'cogs.{extension}')
    print('{} cog loaded'.format(extension.upper()))

bot.run(config.key)
