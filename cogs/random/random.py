import random
import requests

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import check, rubbercog, utils


class Random(rubbercog.Rubbercog):
    """Pick, flip, roll dice"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("random")

    @commands.cooldown(rate=3, per=20.0, type=commands.BucketType.user)
    @commands.check(check.is_verified)
    @commands.command()
    async def pick(self, ctx, *args):
        """"Pick an option"""
        if not len(args):
            return

        option = self.sanitise(random.choice(args), limit=50)
        if option is not None:
            await ctx.send(self.text.get("answer", mention=ctx.author.mention, option=option))

        await utils.room_check(ctx)

    @commands.cooldown(rate=3, per=20.0, type=commands.BucketType.user)
    @commands.check(check.is_verified)
    @commands.command()
    async def flip(self, ctx):
        """Yes/No"""
        option = random.choice(self.text.get("flip"))
        await ctx.send(self.text.get("answer", mention=ctx.author.mention, option=option))
        await utils.room_check(ctx)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.check(check.is_verified)
    @commands.command()
    async def random(self, ctx, first: int, second: int = None):
        """Pick number from interval"""
        if second is None:
            second = 0

        if first > second:
            first, second = second, first

        option = random.randint(first, second)
        await ctx.send(self.text.get("answer", mention=ctx.author.mention, option=option))
        await utils.room_check(ctx)

    @commands.cooldown(rate=5, per=20, type=commands.BucketType.channel)
    @commands.check(check.is_verified)
    @commands.command(aliases=["unsplash"])
    async def picsum(self, ctx, seed: str = None):
        """Get random image from picsum.photos"""
        size = "450/300"
        url = "https://picsum.photos/"
        if seed:
            url += "seed/" + seed + "/"
        url += f"{size}.jpg?random={ctx.message.id}"

        # we cannot use the URL directly, because embed will contain other image than its thumbnail
        image = requests.get(url)
        if image.status_code != 200:
            return await ctx.send(f"E{image.status_code}")

        # get image info
        # example url: https://i.picsum.photos/id/857/600/360.jpg?hmac=.....
        image_id = image.url.split("/id/", 1)[1].split("/")[0]
        image_info = requests.get(f"https://picsum.photos/id/{image_id}/info")
        try:
            image_url = image_info.json()["url"]
        except:
            image_url = discord.Embed.Empty

        embed = self.embed(ctx=ctx, title=discord.Embed.Empty, description=image_url, footer=seed)
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

        await utils.room_check(ctx)


def setup(bot):
    bot.add_cog(Random(bot))
