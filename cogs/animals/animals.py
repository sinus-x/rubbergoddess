import asyncio

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import rubbercog, utils
from core.config import config


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

    @commands.is_owner()
    @commands.command()
    async def animal(self, ctx, member: discord.Member):
        """Send vote embed"""
        await self.check(member, "manual")

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # only act if Gatekeeper cog is not used
        if "Gatekeeper" in self.bot.cogs.keys():
            return

        # only act if their avatar is not default
        if member.avatar_url != member.default_avatar_url:
            await self.check(member, "on_member_join")

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        # only act if user is verified
        member = self.getGuild().get_member(after.id)
        if member is None:
            return

        if "Gatekeeper" in self.bot.cogs.keys() and self.getVerifyRole() not in member.roles:
            return

        if before.avatar_url != after.avatar_url:
            await self.check(after, "on_user_update")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # call if user has been verified
        verify = self.getVerifyRole()
        if verify not in before.roles and verify in after.roles:
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
        animal = self.getChannel().guild.get_member(animal_id)

        for r in message.reactions:
            if r.emoji == "☑️" and r.count > self.config.get("limit"):
                if self.getRole() in animal.roles:
                    # member is an animal and has been before
                    await self.getChannel().send(
                        self.text.get(
                            "result", "yes_yes", nickname=self.sanitise(animal.display_name)
                        )
                    )
                else:
                    # member is an animal and has not been before
                    try:
                        await animal.add_roles(self.getRole())
                        await self.event.user(animal, "New animal!")
                        await self.getChannel().send(
                            self.text.get("result", "no_yes", mention=animal.mention)
                        )
                    except Exception as e:
                        await self.console.error(message, "Could not add animal", e)
                break
            elif r.emoji == "❎" and r.count > self.config.get("limit"):
                if self.getRole() in animal.roles:
                    # member is not an animal and has been before
                    try:
                        await animal.remove_roles(self.getRole())
                        await self.event.user(animal, "Animal left.")
                        await self.getChannel().send(
                            self.text.get("result", "yes_no", mention=animal.mention)
                        )
                    except Exception as e:
                        await self.console.error(message, "Could not remove animal", e)
                else:
                    # member is not an animal and has not been before
                    await self.getChannel().send(
                        self.text.get("result", "no_no", mention=animal.mention)
                    )
                break
        else:
            return
        await utils.delete(message)

    ##
    ## Logic
    ##

    async def check(self, member: discord.Member, source: str):
        """Create vote embed"""
        embed = self.embed(title=self.text.get("title"), description=f"{str(member)} | {member.id}")
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
            await self.event.user(member, "Could not pin Animal check embed.")

        await asyncio.sleep(0.5)
        messages = await message.channel.history(limit=5, after=message).flatten()
        for m in messages:
            if m.type == discord.MessageType.pins_add:
                await utils.delete(m)
                break
