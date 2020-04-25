from random import choice

import discord
from discord.ext import commands

from core import rubbercog, utils
from core.text import text
from config.config import config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

uhoh_counter = 0

class Meme(rubbercog.Rubbercog):
    """Interact with users"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = True

    @commands.Cog.listener()
    async def on_message (self, message):
        global uhoh_counter

        if message.author.bot:
            if self.bot.user.id is not None and \
               message.author.id != self.bot.user.id and \
               message.channel.id not in config.wormhole_distant and \
               message.content.startswith("<:") and \
               message.content.endswith(">"):
                # if another bot has an emoji trigger, say it too
                await message.channel.send(message.content)
            return

        elif config.meme_uhoh in message.content.lower():
            await message.channel.send("uh oh")
            uhoh_counter += 1
        elif message.content == "PR":
            await message.channel.send(messages.git_pr)
        elif message.content == "🔧":
            await message.channel.send(messages.git_issues)
        elif message.content == "🔧👶" or message.content == "🔧 👶":
            link = messages.git_issues.replace("issues", f"labels/easy")
            await message.channel.send(link)

    @commands.command()
    async def uhoh (self, ctx):
        """Say how many 'uh oh's have been said since last boot"""
        await ctx.send(utils.fill_message("uhoh_counter", uhohs=uhoh_counter))

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command(name='??')
    async def question (self, ctx):
        """What?"""
        await ctx.send(choice(messages.question))

    @commands.command()
    async def kachna(self, ctx):
        """Quack"""
        await ctx.send(text.fill("meme", "kachna", url=config.meme_kachna))

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hug (self, ctx, user: discord.Member = None):
        """Hug someone!

        user: Discord user. If none, the bot will hug yourself."""
        if user is None:
            user = ctx.author
        elif user == self.bot.user:
            await ctx.send(emote.hug_left)
            return

        name = user.nick if user.nick else user.name
        await ctx.send(emote.hug_right + f" **{name}**")

    @hug.error
    async def hugError (self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(text.get("error", "no user"))


def setup(bot):
    bot.add_cog(Meme(bot))
