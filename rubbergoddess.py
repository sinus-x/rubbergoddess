import traceback
from datetime import datetime

from discord.ext import commands

from core import help, rubbercog, output, presence, utils
from core.config import config
from repository.database import database
from repository.database import session
from repository.database.karma import Karma, Karma_emoji
from repository.database.seeking import Seeking
from repository.database.review import Review, ReviewRelevance, Subject
from repository.database.verification import User
from repository.database.image import Image
from repository.database.points import Points
from repository.review_repo import ReviewRepository

bot = commands.Bot(command_prefix=config.prefix, help_command=help.Help())

presence = presence.Presence(bot)
event = output.Event(bot)

# fill DB with subjects shortcut, needed for reviews
def load_subjects():
    review_repo = ReviewRepository()
    for subject in config.subjects:
        review_repo.add_subject(subject)


started = False


@bot.event
async def on_ready():
    global started
    if started:
        message = "Reconnected: {timestamp}".format(
            timestamp=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        )
    else:
        message = "Logged in [{level}]: {timestamp} (hash {hash})".format(
            level=config.get("bot", "logging"),
            timestamp=datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            hash=utils.git_hash()[:7],
        )
        started = True

    print(message)
    channel = bot.get_channel(config.get("channels", "stdout"))
    await channel.send(f"```{message}```")
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
    await event.sudo(ctx, f"Loaded: {extension.upper()}")
    print(f"Loaded: {extension.upper()}")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Rozšíření **{extension}** odebráno.")
    await event.sudo(ctx, f"Unloaded: {extension.upper()}")
    print(f"Unloaded: {extension.upper()}")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Rozšíření **{extension}** aktualizováno.")
    await event.sudo(ctx, f"Reloaded: {extension.upper()}")
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
