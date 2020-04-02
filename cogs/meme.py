from random import choice

import discord
from discord.ext import commands

import utils
from config.config import Config as config
from config.messages import Messages as messages

uhoh_counter = 0

class Meme(commands.Cog):
    """Interact with users"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message (self, message):
        global uhoh_counter

        if message.author.bot:
            if self.bot.user.id is not None and \
               message.author.id != self.bot.user.id and \
               message.content.startswith("<:") and \
               message.content.endswith(">"):
                # if another bot has an emoji trigger, say it too
                await message.channel.send(message.content)
            return

        elif config.uhoh_string in message.content.lower():
            await message.channel.send("uh oh")
            uhoh_counter += 1
        elif message.content == "PR":
            await message.channel.send(messages.git_pr)
        elif message.content == "🔧":
            await message.channel.send(messages.git_issues)
        elif message.content == "🔧👶" or message.content == "🔧 👶":
            link = messages.git_issues.replace("issues", f"labels/good%20first%20issue")
            await message.channel.send(link)

    @commands.command()
    async def uhoh (self, ctx):
        """Something is wrong. Say 'uh oh' too"""
        await ctx.send(utils.fill_message("uhoh_counter", uhohs=uhoh_counter))

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command(name='??', aliases=["???"])
    async def question (self, ctx):
        """What?"""
        await ctx.send(choice(messages.question))

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hug (self, ctx, user: discord.Member = None, intensity: int = 0):
        """Hug someone!"""
        if user is None:
            user = ctx.author
        elif user == self.bot.user:
            await ctx.send(emote.hug_left)
            return

        emojis = config.hug_emojis

        user = discord.utils.escape_markdown(user.display_name)
        if 0 <= intensity < len(emojis):
            await ctx.send(emojis[intensity] + f" **{user}**")
        else:
            await ctx.send(choice(emojis) + f" **{user}**")

    @hug.error
    async def hugError (self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(utils.fill_message("meme_hug_not_found", user=ctx.author.id))


def setup(bot):
    bot.add_cog(Meme(bot))
