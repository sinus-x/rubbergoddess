import random
import requests
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List, Union

import discord
from discord.ext import commands

from core.config import config
from cogs.resource import CogConfig, CogText
from core import image_utils, rubbercog, utils
from core.emote import emote
from repository.interaction_repo import InteractionRepository

repo_i = InteractionRepository()


class Meme(rubbercog.Rubbercog):
    """Interact with users"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("meme")
        self.config = CogConfig("meme")

        self.fishing_pool = self.config.get("_fishing")

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, *, target: Union[discord.Member, discord.Role] = None):
        """Hug someone!

        target: Discord user or role. If none, the bot will hug you.
        """
        if target is None:
            hugger = self.bot.user
            hugged = ctx.author
        else:
            hugger = ctx.author
            hugged = target

        if type(hugged) == discord.Role:
            repo_i.add(ctx.guild.id, "hug", hugger.id, None)
        else:
            repo_i.add(ctx.guild.id, "hug", hugger.id, hugged.id)

        await ctx.send(
            emote.hug_right
            + (
                " **" + hugged.display_name + "**"
                if type(target) == discord.Member
                else " ***" + hugged.name + "***"
            )
        )

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def whip(self, ctx, *, user: discord.Member = None):
        """Whip someone"""
        if user is None:
            whipper = self.bot.user
            whipped = ctx.author
        else:
            whipper = ctx.author
            whipped = user

        repo_i.add(ctx.guild.id, "whip", whipper.id, whipped.id)

        async with ctx.typing():
            url = whipped.avatar_url_as(format="jpg")
            response = requests.get(url)
            avatar = Image.open(BytesIO(response.content))

            frames = self.get_whip_frames(avatar)

            with BytesIO() as image_binary:
                frames[0].save(
                    image_binary,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=30,
                    loop=0,
                    transparency=0,
                    disposal=2,
                    optimize=False,
                )
                image_binary.seek(0)
                await ctx.reply(
                    file=discord.File(fp=image_binary, filename="whip.gif"),
                    mention_author=False,
                )

            return

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def spank(self, ctx, *, user: discord.Member = None):
        """Spank someone"""
        if user is None:
            spanker = self.bot.user
            spanked = ctx.author
        else:
            spanker = ctx.author
            spanked = user

        repo_i.add(ctx.guild.id, "spank", spanker.id, spanked.id)

        async with ctx.typing():
            url = spanked.avatar_url_as(format="jpg")
            response = requests.get(url)
            avatar = Image.open(BytesIO(response.content))

            frames = self.get_spank_frames(avatar)

            with BytesIO() as image_binary:
                frames[0].save(
                    image_binary,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=30,
                    loop=0,
                    transparency=0,
                    disposal=2,
                    optimize=False,
                )
                image_binary.seek(0)
                await ctx.reply(
                    file=discord.File(fp=image_binary, filename="spank.gif"),
                    mention_author=False,
                )

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def pet(self, ctx, *, member: discord.Member = None):
        """Pet someone!

        member: Discord user. If none, the bot will pet you.
        """
        if member is None:
            petter = self.bot.user
            petted = ctx.author
        else:
            petter = ctx.author
            petted = member

        repo_i.add(ctx.guild.id, "pet", petter.id, petted.id)

        async with ctx.typing():
            url = petted.avatar_url_as(format="jpg")
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
                await ctx.reply(
                    file=discord.File(fp=image_binary, filename="pet.gif"),
                    mention_author=False,
                )

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def hyperpet(self, ctx, *, member: discord.Member = None):
        """Pet someone really hard

        member: Discord user. If none, the bot will hyperpet you.
        """
        if member is None:
            petter = self.bot.user
            petted = ctx.author
        else:
            petter = ctx.author
            petted = member

        repo_i.add(ctx.guild.id, "hyperpet", petter.id, petted.id)

        async with ctx.typing():
            url = petted.avatar_url_as(format="jpg")
            response = requests.get(url)
            avatar = Image.open(BytesIO(response.content))

            frames = self.get_hyperpet_frames(avatar)

            with BytesIO() as image_binary:
                frames[0].save(
                    image_binary,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=30,
                    loop=0,
                    transparency=0,
                    disposal=2,
                    optimize=False,
                )
                image_binary.seek(0)
                await ctx.reply(
                    file=discord.File(fp=image_binary, filename="hyperpet.gif"),
                    mention_author=False,
                )

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def bonk(self, ctx, *, member: discord.Member = None):
        """Bonk someone

        member: Discord user. If none, the bot will bonk you.
        """
        if member is None:
            bonker = self.bot.user
            bonked = ctx.author
        else:
            bonker = ctx.author
            bonked = member

        repo_i.add(ctx.guild.id, "bonk", bonker.id, bonked.id)

        async with ctx.typing():
            url = bonked.avatar_url_as(format="jpg")
            response = requests.get(url)
            avatar = Image.open(BytesIO(response.content))

            frames = self.get_bonk_frames(avatar)

            with BytesIO() as image_binary:
                frames[0].save(
                    image_binary,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=30,
                    loop=0,
                    transparency=0,
                    disposal=2,
                    optimize=False,
                )
                image_binary.seek(0)
                await ctx.reply(
                    file=discord.File(fp=image_binary, filename="bonk.gif"),
                    mention_author=False,
                )

    @commands.guild_only()
    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.command()
    async def slap(self, ctx, *, member: discord.Member = None):
        """Slap someone!

        member: Discord user. If none, the bot will slap you.
        """
        if member is None:
            slapper = self.bot.user
            slapped = ctx.author
        else:
            slapper = ctx.author
            slapped = member

        options = ["つ", "づ", "ノ"]

        repo_i.add(ctx.guild.id, "slap", slapper.id, slapped.id)

        await ctx.reply(
            "**{}**{} {}".format(
                self.sanitise(slapper.display_name),
                random.choice(options),
                self.sanitise(slapped.display_name),
            ),
            mention_author=False,
        )

    @commands.guild_only()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.command()
    async def relations(self, ctx, *, user: discord.User = None):
        """Get your information about hugs, pets, ..."""
        if user is None:
            user = ctx.author

        embed = self.embed(
            ctx=ctx,
            description=f"**{self.sanitise(user.display_name)}**\n"
            f"{self.text.get('relations_help')}",
        )

        for action in ("hug", "pet", "hyperpet", "slap", "spank", "whip", "bonk"):
            lookup = repo_i.get_user_action(user.id, ctx.guild.id, action)

            if lookup[0] == 0 and lookup[1] == 0:
                continue

            value = self.text.get("value", gave=lookup[0], got=lookup[1])
            embed.add_field(name=f"{config.prefix}{action}", value=value)

        await ctx.reply(embed=embed)
        await utils.room_check(ctx)

    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command(aliases=["owo"])
    async def uwu(self, ctx, *, message: str = None):
        """UWUize message"""
        if message is None:
            text = "OwO!"
        else:
            text = self.sanitise(self.uwuize(message), limit=1900, markdown=True)
        await ctx.send(f"**{self.sanitise(ctx.author.display_name)}**\n>>> " + text)
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
            text = self.sanitise(text[:1900], markdown=True)
        await ctx.send(f"**{self.sanitise(ctx.author.display_name)}**\n>>> " + text)
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
            return await ctx.reply(self.text.get("fishing_fail"))

        await ctx.reply(random.choice(options))

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
            except Exception:
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

        result = " ".join([uwuize_word(s) for s in string.split(" ") if len(s)])
        if result[-1] == "?":
            result += " UwU"
        if result[-1] == "!":
            result += " OwO"
        if result[-1] == ".":
            result = result[:-1] + "," * random.randint(2, 4)

        return result

    @staticmethod
    def round_image(frame_avatar: Image.Image) -> Image.Image:
        """Convert square avatar to circle"""
        frame_mask = Image.new("1", frame_avatar.size, 0)
        draw = ImageDraw.Draw(frame_mask)
        draw.ellipse((0, 0) + frame_avatar.size, fill=255)
        frame_avatar.putalpha(frame_mask)
        return frame_avatar

    @staticmethod
    def get_pet_frames(avatar: Image.Image) -> List[Image.Image]:
        """Get frames for the pet"""
        frames = []
        width, height = 148, 148
        vertical_offset = (0, 0, 0, 0, 1, 2, 3, 4, 5, 4, 3, 2, 2, 1, 0)

        frame_avatar = image_utils.round_image(avatar.resize((100, 100)))

        for i in range(14):
            img = "%02d" % (i + 1)
            frame = Image.new("RGBA", (width, height), (54, 57, 63, 1))
            hand = Image.open(f"data/meme/pet/{img}.png")
            frame.paste(frame_avatar, (35, 25 + vertical_offset[i]), frame_avatar)
            frame.paste(hand, (10, 5), hand)
            frames.append(frame)

        return frames

    @staticmethod
    def get_hyperpet_frames(avatar: Image.Image) -> List[Image.Image]:
        """Get frames for the hyperpet"""
        frames = []
        width, height = 148, 148
        vertical_offset = (0, 1, 2, 3, 1, 0)

        avatar = image_utils.round_image(avatar.resize((100, 100)))
        avatar_pixels = np.array(avatar)
        git_hash = int(utils.git_get_hash(), 16)

        for i in range(6):
            deform_hue = git_hash % 100 ** (i + 1) // 100 ** i / 100
            frame_avatar = Image.fromarray(image_utils.shift_hue(avatar_pixels, deform_hue))

            img = "%02d" % (i + 1)
            frame = Image.new("RGBA", (width, height), (54, 57, 63, 1))
            hand = Image.open(f"data/meme/hyperpet/{img}.png")
            frame.paste(frame_avatar, (35, 25 + vertical_offset[i]), frame_avatar)
            frame.paste(hand, (10, 5), hand)
            frames.append(frame)

        return frames

    @staticmethod
    def get_bonk_frames(avatar: Image.Image) -> List[Image.Image]:
        """Get frames for the bonk"""
        frames = []
        width, height = 200, 170
        deformation = (0, 0, 0, 5, 10, 20, 15, 5)

        avatar = image_utils.round_image(avatar.resize((100, 100)))

        for i in range(8):
            img = "%02d" % (i + 1)
            frame = Image.new("RGBA", (width, height), (54, 57, 63, 1))
            bat = Image.open(f"data/meme/bonk/{img}.png")

            frame_avatar = avatar.resize((100, 100 - deformation[i]))

            frame.paste(frame_avatar, (80, 60 + deformation[i]), frame_avatar)
            frame.paste(bat, (10, 5), bat)
            frames.append(frame)

        return frames

    @staticmethod
    def get_whip_frames(avatar: Image.Image) -> List[Image.Image]:
        """Get frames for the whip"""
        frames = []
        width, height = 250, 150
        deformation = (0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 5, 9, 6, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        translation = (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 3, 3, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        avatar = image_utils.round_image(avatar.resize((100, 100)))

        for i in range(26):
            img = "%02d" % (i + 1)
            frame = Image.new("RGBA", (width, height), (54, 57, 63, 1))
            whip_frame = Image.open(f"data/meme/whip/{img}.png").resize((150, 150))

            frame_avatar = avatar.resize((100 - deformation[i], 100))

            frame.paste(frame_avatar, (135 + deformation[i] + translation[i], 25), frame_avatar)
            frame.paste(whip_frame, (0, 0), whip_frame)
            frames.append(frame)

        return frames

    @staticmethod
    def get_spank_frames(avatar: Image.Image) -> List[Image.Image]:
        """Get frames for the spank"""
        frames = []
        width, height = 200, 120
        deformation = (4, 2, 1, 0, 0, 0, 0, 3)

        avatar = image_utils.round_image(avatar.resize((100, 100)))

        for i in range(8):
            img = "%02d" % (i + 1)
            frame = Image.new("RGBA", (width, height), (54, 57, 63, 1))
            spoon = Image.open(f"data/meme/spank/{img}.png").resize((100, 100))

            frame_avatar = avatar.resize((100 + 2 * deformation[i], 100 + 2 * deformation[i]))

            frame.paste(spoon, (10, 15), spoon)
            frame.paste(frame_avatar, (80 - deformation[i], 10 - deformation[i]), frame_avatar)
            frames.append(frame)

        return frames
