import asyncio
import requests
import tempfile
from io import BytesIO
from datetime import datetime
from PIL import Image

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, image_utils, rubbercog, utils
from repository import user_repo

repo_u = user_repo.UserRepository()


class Animals(rubbercog.Rubbercog):
    """Private zone"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("animals")
        self.text = CogText("animals")

        self.channel = None
        self.role = None

    def getChannel(self):
        if self.channel is None:
            self.channel = self.bot.get_channel(self.config.get("channel"))
        return self.channel

    def getRole(self):
        if self.role is None:
            self.role = self.getChannel().guild.get_role(self.config.get("role"))
        return self.role

    ##
    ## Commands
    ##

    @commands.check(acl.check)
    @commands.command()
    async def animal(self, ctx, member: discord.Member):
        """Send vote embed"""
        await self.check(member, "manual")

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        # only act if user is verified
        member = self.getGuild().get_member(after.id)
        if member is None:
            return

        # only act if user is verified
        if self.getVerifyRole() not in member.roles:
            return

        # only act if user has changed their avatar
        if before.avatar_url == after.avatar_url:
            return

        await self.check(after, "on_user_update")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # only act if the user has been verified
        verify = self.getVerifyRole()
        if not (verify not in before.roles and verify in after.roles):
            return

        # only act if their avatar is not default
        if after.avatar_url == after.default_avatar_url:
            await self.console.debug(f"{after} verified", "Not an animal (default avatar).")
            return

        # lookup user timestamp, only allow new verifications
        db_user = repo_u.get(after.id)
        if db_user is not None and db_user.status == "verified":
            db_user = repo_u.get(after.id)
            timestamp = datetime.strptime(db_user.changed, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            if (now - timestamp).total_seconds() > 5:
                # this was probably temporary unverify, they have been checked before
                await self.console.debug(f"{after} reverified", "Skipping (unverify).")
                return

        await self.check(after, "on_member_update")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Vote"""
        if payload.channel_id != self.getChannel().id:
            return

        if payload.member.bot:
            return

        message = await self.getChannel().fetch_message(payload.message_id)
        # fmt: off
        if not message or len(message.embeds) != 1 \
        or message.embeds[0].title != self.text.get("title"):
            return
        # fmt: on

        if str(payload.emoji) not in ("☑️", "❎"):
            return await message.remove_reaction(payload.emoji, payload.member)

        animal_id = int(message.embeds[0].description.split(" | ")[1])
        if animal_id == payload.member.id:
            return await message.remove_reaction(payload.emoji, payload.member)
        animal = await self.getChannel().guild.fetch_member(animal_id)

        if animal is None:
            await self.console.error(
                "animals", f"Could not find member with ID {animal_id}. Vote aborted."
            )
            await self.console.info("animals", f"Could not find user {animal_id}, vote aborted.")
            return await utils.delete(message)

        # delete if the user has changed their avatar since the embed creation
        if str(message.embeds[0].image.url) != str(animal.avatar_url):
            await self.console.debug(animal, "Avatar has changed since. Vote aborted.")
            return await utils.delete(message)

        animal_avatar_url = animal.avatar_url_as(format="jpg")
        animal_avatar_data = requests.get(animal_avatar_url)
        animal_avatar = Image.open(BytesIO(animal_avatar_data.content))
        animal_avatar_file = tempfile.TemporaryFile()

        for r in message.reactions:
            if r.emoji == "☑️" and r.count > self.config.get("limit"):
                avatar_result: Image.Image = Animals.add_border(animal_avatar, 3, True)
                avatar_result.save(animal_avatar_file, "png")
                animal_avatar_file.seek(0)
                if self.getRole() in animal.roles:
                    # member is an animal and has been before
                    await self.getChannel().send(
                        self.text.get(
                            "result",
                            "yes_yes",
                            nickname=self.sanitise(animal.display_name),
                        ),
                        file=discord.File(fp=animal_avatar_file, filename="animal.png"),
                    )
                else:
                    # member is an animal and has not been before
                    try:
                        await animal.add_roles(self.getRole())
                        await self.event.user(animal, "New animal!")
                        await self.getChannel().send(
                            self.text.get("result", "no_yes", mention=animal.mention),
                            file=discord.File(fp=animal_avatar_file, filename="animal.png"),
                        )
                    except Exception as e:
                        await self.console.error(message, "Could not add animal", e)
                break
            elif r.emoji == "❎" and r.count > self.config.get("limit"):
                avatar_result: Image.Image = Animals.add_border(animal_avatar, 3, False)
                avatar_result.save(animal_avatar_file, "png")
                animal_avatar_file.seek(0)
                if self.getRole() in animal.roles:
                    # member is not an animal and has been before
                    try:
                        await animal.remove_roles(self.getRole())
                        await self.event.user(animal, "Animal left.")
                        await self.getChannel().send(
                            self.text.get("result", "yes_no", mention=animal.mention),
                            file=discord.File(fp=animal_avatar_file, filename="animal.png"),
                        )
                    except Exception as e:
                        await self.console.error(message, "Could not remove animal", e)
                else:
                    # member is not an animal and has not been before
                    await self.getChannel().send(
                        self.text.get("result", "no_no", mention=animal.mention),
                        file=discord.File(fp=animal_avatar_file, filename="animal.png"),
                    )
                break
        else:
            return

        # Edit original message
        result = [0, 0]
        for r in message.reactions:
            if r.emoji == "☑️":
                result[0] = r.count - 1
            elif r.emoji == "❎":
                result[1] = r.count - 1

        await message.edit(
            embed=None,
            content=self.text.get(
                "edit", nickname=self.sanitise(animal.display_name), yes=result[0], no=result[1]
            ),
        )
        try:
            await message.unpin()
        except Exception as e:
            await self.console.error(message, "Could not unpin Animal vote embed", e)

    ##
    ## Logic
    ##

    async def check(self, member: discord.Member, source: str):
        """Create vote embed"""
        embed = self.embed(
            title=self.text.get("title"),
            description=f"{self.sanitise(str(member))} | {member.id}",
        )
        embed.add_field(
            name=self.text.get("source", source),
            value=self.text.get("required", limit=self.config.get("limit")),
            inline=False,
        )
        embed.set_image(url=member.avatar_url)
        message = await self.getChannel().send(embed=embed)
        await message.add_reaction("☑️")
        await message.add_reaction("❎")

        try:
            await message.pin()
        except Exception as e:
            await self.console.warning(member, "Could not pin Animal check embed.", e)

        await asyncio.sleep(0.5)
        messages = await message.channel.history(limit=5, after=message).flatten()
        for m in messages:
            if m.type == discord.MessageType.pins_add:
                await utils.delete(m)
                break

    @staticmethod
    def add_border(image: Image.Image, border: int, animal: bool) -> Image.Image:
        """Add border to created image.

        image: The avatar.
        border: width of the border.
        animal: whether the avatar is an animal or not.
        """
        image_size = 160
        frame_color = (22, 229, 0, 1) if animal else (221, 56, 31, 1)
        frame = Image.new("RGBA", (image_size + border * 2, image_size + border * 2), frame_color)
        frame = image_utils.round_image(frame)
        avatar = image_utils.round_image(image.resize((image_size, image_size)))
        frame.paste(avatar, (border, border), avatar)
        return frame
