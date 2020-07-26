import discord
from discord.ext import commands

from cogs.resource import CogText
from core import rubbercog, utils
from core.emote import emote


class Meme(rubbercog.Rubbercog):
    """Interact with users"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("meme")

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """Hug someone!

        user: Discord user. If none, the bot will hug yourself.
        """
        if user is None:
            user = ctx.author
        elif user == self.bot.user:
            await ctx.send(emote.hug_left)
            return

        await ctx.send(emote.hug_right + f" **{self.sanitise(user.display_name)}**")

    @hug.error
    async def hugError(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(self.text.get("cannot_hug"))

    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command(aliases=["owo"])
    async def uwu(self, ctx, *, message: str = None):
        """UWUize message"""
        await utils.delete(ctx)

        if message is None:
            text = "OwO!"
        else:
            text = self.sanitise(self.uwuize(message), limit=1960, markdown=True)
        await ctx.send(ctx.author.mention + " " + text)

    ##
    ## Logic
    ##

    @staticmethod
    def uwuize(string: str) -> str:
        # Adapted from https://github.com/PhasecoreX/PCXCogs/blob/master/uwu/uwu.py
        result = []

        def uwuize_word(string: str) -> str:
            try:
                if string.lower()[0] == "m" and len(string) > 2:
                    w = "W" if string[1].isupper() else "w"
                    string = string[0] + w + string[1:]
            except:
                # this is how we handle emojis
                pass
            string = string.replace("r", "w").replace("R", "W")
            string = string.replace("ř", "w").replace("Ř", "W")
            string = string.replace("l", "w").replace("L", "W")

            return string

        result = " ".join([uwuize_word(s) for s in string.split(" ")])
        if result[-1] == "?":
            result += " UwU"
        if result[-1] == "!":
            result += " OwO"

        return result
