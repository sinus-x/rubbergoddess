import traceback
from datetime import datetime
import logging


class DiscordLogFilter(logging.Filter):
    def filter(self, record):
        # See https://github.com/Rapptz/discord.py/blob/
        # 1bf7aadf943844ed5970a9d44b73d1d67b790b08/discord/http.py#L221
        # and below.
        return "rate limit" in record.msg


discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.DEBUG)
discord_logger_handler = logging.StreamHandler()
discord_logger_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
discord_logger_handler.addFilter(DiscordLogFilter())
discord_logger.addHandler(discord_logger_handler)


import discord
from discord.ext import commands

from core import acl, help, rubbercog, output, utils
from core.config import config
from repository.database import database
from repository.database import session
from repository.database.acl import ACL_group, ACL_rule, ACL_rule_user, ACL_rule_group
from repository.database.anonsend import AnonsendChannel
from repository.database.image import Image
from repository.database.karma import Karma, Karma_emoji
from repository.database.interactions import Interaction
from repository.database.points import Points
from repository.database.review import Review, ReviewRelevance, Subject
from repository.database.seeking import Seeking
from repository.database.verification import User
from repository.review_repo import ReviewRepository

intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.bans = True  # Used for database update
intents.emojis = True  # Used for Karma
intents.voice_states = True  # Used for Voice
intents.messages = True  # Used all over the place
intents.reactions = True  # Used for Karma and scrolling
intents.presences = True

bot = commands.Bot(
    command_prefix=config.prefix,
    help_command=help.Help(),
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
    intents=intents,
)

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
        message = "Logged in [{level}]: {timestamp} ({hash} on branch {branch})".format(
            level=config.get("bot", "logging"),
            timestamp=datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            hash=utils.git_get_hash()[:7],
            branch=utils.git_get_branch(),
        )
        started = True

    print(message)
    channel = bot.get_channel(config.get("channels", "stdout"))
    await channel.send(f"```{message}```")
    await utils.set_presence(bot, status=discord.Status.online)


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
@commands.check(acl.check)
async def load(ctx, *, extensions: str):
    """Load modules"""
    for extension in extensions.split(" "):
        bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Rozšíření **{extension}** načteno.")
        await event.sudo(ctx, f"Loaded: {extension.upper()}")
        print(f"Loaded: {extension.upper()}.")


@bot.command()
@commands.check(acl.check)
async def unload(ctx, *, extensions: str):
    """Unload modules"""
    for extension in extensions.split(" "):
        bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Rozšíření **{extension}** odebráno.")
        await event.sudo(ctx, f"Unloaded: {extension.upper()}")
        print(f"Unloaded: {extension.upper()}.")


@bot.command()
@commands.check(acl.check)
async def reload(ctx, *, extensions: str):
    """Reload modules"""
    for extension in extensions.split(" "):
        bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Rozšíření **{extension}** aktualizováno.")
        await event.sudo(ctx, f"Reloaded: {extension.upper()}")
        print(f"Reloaded: {extension.upper()}.")


# database.base.metadata.drop_all(database.db)
database.base.metadata.create_all(database.db)
session.commit()  # Making sure

load_subjects()

bot.load_extension("cogs.errors")
print("Loaded: ERRORS (implicit)")
bot.load_extension("cogs.acl")
print("Loaded: ACL (implicit)")
for extension in config.extensions:
    bot.load_extension(f"cogs.{extension}")
    print(f"Loaded: {extension.upper()}")

bot.run(config.key)
