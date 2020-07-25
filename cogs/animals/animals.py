import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import check, rubbercog, utils


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

    ##
    ## Listeners
    ##

    # TODO Only act if Gatekeeper is not active
    #      Else, check for verify role being added
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.check(member)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar_url != after.avatar_url:
            await self.check(after)

    # TODO rewrite to on_raw_reaction_add
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Vote"""
        if user.bot:
            return

        if reaction.message.channel != self.getChannel():
            return

        # fmt: off
        if len(reaction.message.embeds) != 1 \
        or reaction.message.embeds[0].title != self.text.get("title"):
            return
        # fmt: on

        if str(reaction.emoji) not in ("☑️", "❎"):
            return await utils.remove_reaction(reaction, user)

        member_id = int(reaction.message.embeds[0].description.split(" | ")[1])
        member = reaction.message.guild.get_member(member_id)

        for r in reaction.message.reactions:
            if r.emoji == "☑️" and r.count > self.config.get("limit"):
                await member.add_roles(self.getRole())
                await self.event.user(member, "New animal!")
                await self.getChannel().send(self.text.get("join", mention=member.mention))
                break
            elif r.emoji == "❎" and r.count > self.config.get("limit"):
                await member.remove_roles(self.getRole())
                # TODO Log event only if user had `animal` role
                await self.event.user(member, "Animal left.")
                await self.getChannel().send(self.text.get("leave", mention=member.mention))
                break
        else:
            return
        await utils.delete(reaction.message)

    ##
    ## Logic
    ##

    async def check(self, member: discord.Member):
        # create embed
        embed = self.embed(title=self.text.get("title"), description=f"{str(member)} | {member.id}")
        embed.add_field(
            name="\u200b", value=self.text.get("required", limit=self.config.get("limit"))
        )
        embed.set_image(url=member.avatar_url)
        message = await self.getChannel().send(embed=embed)
        await message.add_reaction("☑️")
        await message.add_reaction("❎")
        try:
            await message.pin()
        except Exception as e:
            await self.event.user(member, "Could not pin Animal check embed.")
            await self.console.warning("animals", "Could not unpin embed", e)
