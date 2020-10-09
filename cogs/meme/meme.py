import random
import requests
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw
from typing import Union

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import rubbercog, image_utils, utils
from core.emote import emote


class Meme(rubbercog.Rubbercog):
    """Interact with users"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("meme")
        self.config = CogConfig("meme")

        self.fishing_pool = self.config.get("_fishing")

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

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def pet(self, ctx, member: discord.Member = None):
        """Pet someone!

        member: Discord user. If none, the bot will hug yourself.
        """
        if member is None:
            member = ctx.author

        async with ctx.typing():
            url = member.avatar_url_as(format="jpg")
            response = requests.get(url)
            avatar = Image.open(BytesIO(response.content))

            frames = self.get_pet_frames(avatar)

            with BytesIO() as image_binary:
                frames[0].save(
                    image_binary,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=40,
                    loop=0,
                    transparency=0,
                    disposal=2,
                    optimize=False,
                )
                image_binary.seek(0)
                filename = self.get_pet_name(member)
                await ctx.send(file=discord.File(fp=image_binary, filename=filename))

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hyperpet(self, ctx, member: discord.Member = None):
        """Pet someone really hard

        member: Discord user. If none, the bot will hug yourself.
        """
        if member is None:
            member = ctx.author

        async with ctx.typing():
            url = member.avatar_url_as(format="jpg")
            response = requests.get(url)
            avatar = Image.open(BytesIO(response.content))

            frames = self.get_pet_frames(avatar, hue=True)

            with BytesIO() as image_binary:
                frames[0].save(
                    image_binary,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=40,
                    loop=0,
                    transparency=0,
                    disposal=2,
                    optimize=False,
                )
                image_binary.seek(0)
                filename = self.get_pet_name(member)
                await ctx.send(file=discord.File(fp=image_binary, filename=filename))

    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command(aliases=["owo"])
    async def uwu(self, ctx, *, message: str = None):
        """UWUize message"""
        if message is None:
            text = "OwO!"
        else:
            text = self.sanitise(self.uwuize(message), limit=1900, markdown=True)
        await ctx.send(f"**{ctx.author.display_name}**\n>>> " + text)
        await utils.delete(ctx.message)

    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command(aliases=["rcase", "randomise"])
    async def randomcase(self, ctx, *, message: str = None):
        """raNdOMisE cAsInG"""
        if message is None:
            text = "O.o"
        else:
            text = ""
            for letter in message:
                if letter.isalpha():
                    text += letter.upper() if random.choice((True, False)) else letter.lower()
                else:
                    text += letter
        await ctx.send(f"**{ctx.author.display_name}**\n>>> " + text[:1900])
        await utils.delete(ctx.message)

    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @commands.command()
    async def fish(self, ctx):
        """Go fishing!"""
        roll = random.uniform(0, 1)
        options = None
        for probabilty, harvest in self.fishing_pool.items():
            if roll >= float(probabilty):
                options = harvest
                break
        else:
            return await ctx.send(self.text.get("fishing_fail", mention=ctx.author.mention))

        await ctx.send(random.choice(options))

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
            string = string.replace("?", "?" * random.randint(1, 3))
            string = string.replace("'", ";" * random.randint(1, 3))
            if string[-1] == ",":
                string = string[:-1] + "." * random.randint(2, 3)

            return string

        result = " ".join([uwuize_word(s) for s in string.split(" ")])
        if result[-1] == "?":
            result += " UwU"
        if result[-1] == "!":
            result += " OwO"
        if result[-1] == ".":
            result = result[:-1] + "," * random.randint(2, 4)

        return result

    @staticmethod
    def get_pet_frames(self, avatar: Image, hue: bool = False) -> list:
        """Get frames for the pet

        avatar: Image
        hue: boolean; if set to True, avatar's hue is randomly offset
        """
        frames = []
        deform_width = (-1, -2, 1, 2, 1)
        defom_height = (4, 3, 2, 2, -4)
        width, height = 80, 80

        if hue:
            git_hash = int(utils.git_get_hash(), 16)
            avatar_pixels = np.array(avatar)
        else:
            git_hash = None
            avatar_pixels = None

        for i in range(5):
            if hue:
                # get random values based on current hash -- last ten decimal digits
                deform_hue = git_hash % 100 ** (i + 1) // 100 ** i / 100
                avatar = Image.fromarray(image_utils.shift_hue(avatar_pixels, deform_hue))

            frame = Image.new("RGBA", (112, 112), (255, 255, 255, 1))
            hand = Image.open(f"data/meme/pet_{i}.png")
            width -= deform_width[i]
            height -= defom_height[i]
            frame_avatar = avatar.resize((width, height))
            frame_mask = Image.new("1", frame_avatar.size, 0)
            draw = ImageDraw.Draw(frame_mask)
            draw.ellipse((0, 0) + frame_avatar.size, fill=255)
            frame_avatar.putalpha(frame_mask)

            frame.paste(frame_avatar, (112 - width, 112 - height), frame_avatar)
            frame.paste(hand, (0, 0), hand)
            frames.append(frame)

        return frames

    @staticmethod
    def get_pet_name(self, author: Union[discord.Member, discord.User]) -> str:
        """Get virtual filename for the pet gif"""
        return f"PetThe{author.display_name.replace(' ', '')}.gif"
