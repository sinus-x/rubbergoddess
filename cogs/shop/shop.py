import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from repository import user_repo, karma_repo

repo_u = user_repo.UserRepository()
repo_k = karma_repo.KarmaRepository()


class Shop(rubbercog.Rubbercog):
    """Make use of your karma"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("shop")
        self.text = CogText("shop")

    @commands.command()
    async def shop(self, ctx):
        """Display prices for various services"""
        embed = self.embed(
            ctx=ctx,
            title=self.text.get("info", "change"),
            description=self.text.get("info", "description"),
        )

        embed.add_field(
            name=self.text.get("info", "set"),
            value=self.config.get("set"),
        )
        embed.add_field(
            name=self.text.get("info", "reset"),
            value=self.config.get("reset"),
        )

        await ctx.send(embed=embed)
        await utils.room_check(ctx)

    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.check(acl.check)
    @commands.group(name="nickname")
    async def nickname(self, ctx):
        """Change your nickname"""
        await utils.send_help(ctx)

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @commands.check(acl.check)
    @nickname.command(name="set")
    async def nickname_set(self, ctx, *, nick: str):
        """Set the nickname. Use command `shop` to see prices

        Attributes
        ----------
        nick: Your new nickname
        """
        # stop if user does not have nickname set
        if ctx.author.nick is None and nick is None or not len(nick):
            return await ctx.send(self.text.get("no_nick", mention=ctx.author.mention))

        # check if user has karma
        if self.get_user_karma(ctx.author.id) < self.config.get("set"):
            return await ctx.send(
                self.text.get(
                    "not_enough_karma",
                    mention=ctx.author.mention,
                )
            )

        for char in ("@", "#", "`", "'", '"'):
            if char in nick:
                return await ctx.send(self.text.get("bad_character"))

        # set nickname
        try:
            await ctx.author.edit(nick=nick, reason="Nickname purchase")
        except discord.Forbidden:
            return await ctx.send(self.text.get("higher_role"))

        repo_k.updateMemberKarma(ctx.author.id, -1 * self.price_nick)
        await ctx.send(
            self.text.get(
                "new_nick",
                mention=ctx.author.mention,
                nick=discord.utils.escape_markdown(nick),
                value=self.price_nick,
            )
        )
        await self.event.user(ctx, f"Nickname changed to {nick}.")

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @commands.check(acl.check)
    @nickname.command(name="unset")
    async def nickname_unset(self, ctx):
        """Unset the nickname"""
        if ctx.author.nick is None:
            return await ctx.send(self.text.get("no_nick", mention=ctx.author.mention))

        # check if user has karma
        if self.get_user_karma(ctx.author.id) < self.config.get("reset"):
            return await ctx.send(
                self.text.get(
                    "not_enough_karma",
                    mention=ctx.author.mention,
                )
            )

        nick = ctx.author.nick

        await ctx.author.edit(nick=None, reason="Nickname reset")
        await ctx.send(
            self.text.get(
                "nick_removed",
                mention=ctx.author.mention,
                nick=self.sanitise(nick),
            )
        )
        await self.event.user(ctx, "Nickname reset.")

    ##
    ## Logic
    ##

    def get_user_karma(self, user_id: int) -> int:
        return getattr(repo_k.getMember(user_id), "karma", 0)
