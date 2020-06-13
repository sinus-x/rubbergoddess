import traceback
from datetime import datetime

from discord.ext import commands

from core import help, rubbercog, output
from core.config import config
from features import presence
from repository.database import database
from repository.database import session
from repository.database.karma import Karma, Karma_emoji
from repository.database.review import Review, ReviewRelevance, Subject
from repository.database.verification import User
from repository.database.image import Image
from repository.review_repo import ReviewRepository

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*config.prefixes), help_command=help.Help()
)

presence = presence.Presence(bot)
event = output.Event(bot)

# fill DB with subjects shortcut, needed for reviews
def load_subjects():
    review_repo = ReviewRepository()
    for subject in config.subjects:
        review_repo.add_subject(subject)


@bot.event
async def on_ready():
    """If Rubbergoddess is ready"""
    login = f"Logged in [{config.get('bot', 'logging')}]: "
    print(login + datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    await presence.set_presence()


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(config.channel_botdev)
    output = traceback.format_exc()
    print(output)
    output = list(output[0 + i : 1960 + i] for i in range(0, len(output), 1960))
    if channel is not None:
        for message in output:
            await channel.send("```\n{}```".format(message))


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Rozšíření **{extension}** načteno.")
    await event.sudo(ctx.author, ctx.channel, f"Loaded: {extension.upper()}")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Rozšíření **{extension}** odebráno.")
    await event.sudo(ctx.author, ctx.channel, f"Unloaded: {extension.upper()}")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Rozšíření **{extension}** aktualizováno.")
    await event.sudo(ctx.author, ctx.channel, f"Reloaded: {extension.upper()}")
    print(f"Reloaded: {extension.upper()}")
    if "docker" in config.loader:
        await ctx.send("Jsem ale zavřená v Dockeru, víš o tom?")


# database.base.metadata.drop_all(database.db)
database.base.metadata.create_all(database.db)
session.commit()  # Making sure

load_subjects()

bot.load_extension("cogs.errors")
print("Loaded: ERRORS (implicit)")
for extension in config.extensions:
    bot.load_extension(f"cogs.{extension}")
    print(f"Loaded: {extension.upper()}")

bot.run(config.key)
